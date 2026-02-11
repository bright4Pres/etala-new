from django.contrib import admin
from .models import BorrowHistory, Book, BookCopy, grade_Seven, grade_Eight, grade_Nine, grade_Ten, grade_Eleven, grade_Twelve, StudentActivation
from django.urls import path, reverse
from django.shortcuts import redirect, get_object_or_404, render
from django.utils import timezone
from django.utils.html import format_html
from django.http import HttpResponse
from django.core.management import call_command
from django.contrib import messages
import csv
from io import StringIO, BytesIO
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import base64

# Inline admin for BookCopy - allows adding copies when editing a Book
class BookCopyInline(admin.TabularInline):
    model = BookCopy
    extra = 3  # Show 3 empty copy forms by default
    fields = ['accessionNumber', 'Location', 'status']
    verbose_name = "Book Copy"
    verbose_name_plural = "Physical Copies"

class CirculationAdmin(admin.ModelAdmin):
    change_list_template = "admin/circulation_change_list.html"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset

class BulkImportAdmin(admin.ModelAdmin):
    """Base admin class for grade tables with CSV import functionality."""
    change_list_template = "admin/bulk_import_changelist.html"
    
    def changelist_view(self, request, extra_context=None):
        """Add import/export URLs to changelist context."""
        extra_context = extra_context or {}
        import_url = reverse(f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_import_csv')
        download_url = reverse(f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_download_template')
        extra_context['import_url'] = import_url
        extra_context['download_url'] = download_url
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv_view), name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_import_csv"),
            path('download-template/', self.admin_site.admin_view(self.download_template_view), name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_download_template"),
        ]
        return custom_urls + urls

    def download_template_view(self, request):
        """Generate and download a CSV template."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="student_template_{self.model._meta.model_name}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['name', 'school_id', 'email', 'gender'])
        writer.writerow(['John Doe', 'S12345', 'john@example.com', 'Male'])
        writer.writerow(['Jane Smith', 'S12346', 'jane@example.com', 'Female'])
        
        return response

    def import_csv_view(self, request):
        """Handle CSV file upload and import."""
        if request.method == 'POST' and request.FILES.get('csv_file'):
            try:
                csv_file = request.FILES['csv_file']
                decoded_file = csv_file.read().decode('utf-8')
                reader = csv.DictReader(StringIO(decoded_file))
                
                imported_count = 0
                errors = []
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
                    try:
                        # Expected columns: name, school_id, gender, email
                        student = self.model(
                            name=row.get('name', '').strip(),
                            school_id=row.get('school_id', '').strip(),
                            gender=row.get('gender', 'Other').strip(),
                            email=row.get('email', '').strip(),
                        )
                        student.full_clean()
                        student.save()
                        imported_count += 1
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                
                # Render confirmation page
                context = {
                    'imported_count': imported_count,
                    'errors': errors,
                    'model_name': self.model._meta.verbose_name_plural,
                }
                return render(request, 'admin/import_complete.html', context)
                
            except Exception as e:
                return render(request, 'admin/import_error.html', {'error': str(e)})
        
        return render(request, 'admin/import_csv.html')
class GradeAdminBase(BulkImportAdmin):
    """Base class for grade admins with activation status display."""
    search_fields = ['name', 'email', 'school_id']
    list_display = ['name', 'school_id', 'email', 'gender', 'activation_status', 'created_at']
    actions = ['move_up_all_students']
    
    def activation_status(self, obj):
        """Display activation status with color."""
        if obj.is_activated:
            return format_html('<span style="color: green; font-weight: bold;">Activated</span>')
        else:
            return format_html('<span style="color: orange; font-weight: bold;">Pending</span>')
    activation_status.short_description = "Status"
    
    def move_up_all_students(self, request, queryset):
        """Admin action to move all students up one grade level."""
        if 'confirm' in request.POST:
            # User confirmed - execute the move-up
            from io import StringIO
            output = StringIO()
            
            try:
                # Call the management command
                call_command('moveup_students', stdout=output)
                output_str = output.getvalue()
                
                # Display success message with summary
                messages.success(request, f"Students moved up successfully!\n\n{output_str}")
                return redirect(request.get_full_path())
                
            except Exception as e:
                messages.error(request, f"Error during move-up: {str(e)}")
                return redirect(request.get_full_path())
        
        # Show confirmation page
        return render(request, 'admin/moveup_confirmation.html', {
            'title': 'Confirm Student Grade Move-Up',
            'action': 'move_up_all_students',
            'opts': self.model._meta,
        })
    
    move_up_all_students.short_description = "Move All Students Up One Grade"

class grade_SevenAdmin(GradeAdminBase):
    pass

class grade_EightAdmin(GradeAdminBase):
    pass

class grade_NineAdmin(GradeAdminBase):
    pass

class grade_TenAdmin(GradeAdminBase):
    pass

class grade_ElevenAdmin(GradeAdminBase):
    pass

class grade_TwelveAdmin(GradeAdminBase):
    pass

class historyAdmin(admin.ModelAdmin):
    search_fields = ['bookID', 'accountID', 'bookTitle', 'accountName', 'borrow_date', 'return_date', 'returned']
    list_display = ['bookID', 'bookTitle', 'accountID', 'accountName', 'borrow_date', 'return_date', 'returned', 'return_action']
    list_filter = ['bookID', 'accountID', 'borrow_date', 'return_date', 'returned']
    ordering = ['borrow_date']

    def get_urls(self):
        """Register a custom URL for marking books as returned."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "mark-returned/<int:history_id>/",
                self.admin_site.admin_view(self.mark_returned_view),
                name="lims_app_borrowhistory_mark_returned",
            ),
        ]
        return custom_urls + urls

    def return_action(self, obj):
        """Display a 'Mark as Returned' button if not yet returned."""
        if not obj.returned:
            url = reverse('admin:lims_app_borrowhistory_mark_returned', args=[obj.pk])
            return format_html('<a class="button" href="{}">Return</a>', url)
        return "-"
    return_action.short_description = "Return"

    def mark_returned_view(self, request, history_id):
        """Handle the 'Mark as Returned' action."""
        history = get_object_or_404(BorrowHistory, pk=history_id)
        history.returned = True
        history.save()

        # Update BookCopy model
        try:
            book_copy = BookCopy.objects.get(accessionNumber=history.bookID)
            book_copy.status = "Available"
            book_copy.borrowed_by = None
            book_copy.student_id = None
            book_copy.borrow_date = None
            book_copy.return_date = None
            book_copy.save()
        except BookCopy.DoesNotExist:
            pass

        # Redirect back to the BorrowHistory changelist
        return redirect('admin:lims_app_borrowhistory_changelist')
    
class StudentActivationAdmin(admin.ModelAdmin):
    search_fields = ['name', 'email', 'school_id']
    list_display = ['name', 'school_id', 'email', 'grade', 'is_activated', 'activation_status']
    list_filter = ['is_activated', 'grade', 'created_at']
    readonly_fields = ['otp', 'otp_created_at', 'activated_at', 'created_at']
    
    def activation_status(self, obj):
        """Display activation status with color."""
        if obj.is_activated:
            return format_html('<span style="color: green;">✓ Activated</span>')
        elif obj.otp and not obj.is_otp_expired():
            return format_html('<span style="color: orange;">⏳ Pending (OTP Valid)</span>')
        else:
            return format_html('<span style="color: red;">⏹ Pending</span>')
    activation_status.short_description = "Status"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('resend-otp/<int:activation_id>/', self.admin_site.admin_view(self.resend_otp_view), name="lims_app_studentactivation_resend_otp"),
        ]
        return custom_urls + urls
    
    def resend_otp_view(self, request, activation_id):
        """Resend OTP to student."""
        from .tasks import send_otp_email_task
        
        activation = get_object_or_404(StudentActivation, pk=activation_id)
        otp = activation.generate_otp()
        
        # Send OTP via Celery task (async)
        send_otp_email_task.delay(activation.email, otp, activation.name)
        
        self.message_user(request, f"OTP resent to {activation.email}")
        return redirect('admin:lims_app_studentactivation_changelist')

class BookAdmin(admin.ModelAdmin):
    search_fields = ['Title', 'mainAuthor', 'coAuthor', 'callNumber', 'Publisher']
    list_display = ['Title', 'mainAuthor', 'coAuthor', 'Publisher', 'Edition', 'callNumber', 'Language', 'Type', 'total_copies_display', 'available_copies_display']
    list_filter = ['Language', 'Type']
    inlines = [BookCopyInline]  # Add copies inline when editing a book
    
    def total_copies_display(self, obj):
        return obj.get_total_copies()
    total_copies_display.short_description = 'Total Copies'
    
    def available_copies_display(self, obj):
        return obj.get_available_copies()
    available_copies_display.short_description = 'Available'

class BookCopyAdmin(admin.ModelAdmin):
    change_list_template = "admin/book_change_list.html"
    search_fields = ['book__Title', 'book__mainAuthor', 'accessionNumber', 'Location']
    list_display = ['accession_number_barcode', 'book', 'Location', 'status', 'borrowed_by', 'student_id', 'borrow_date', 'return_date', 'approve_request']
    list_filter = ['status', 'Location']
    raw_id_fields = ['book']

    def generate_barcode_image(self, accession_number):
        """Generate a barcode image and return as base64 data URL."""
        try:
            # Create barcode
            code128 = barcode.get('code128', accession_number, writer=ImageWriter())
            
            # Adjust parameters based on length for better display
            length = len(str(accession_number))
            if length <= 5:
                # For short codes, make barcode wider and taller
                module_width = 0.5
                module_height = 12.0
                quiet_zone = 2.0
            else:
                # Default parameters for longer codes
                module_width = 0.3
                module_height = 8.0
                quiet_zone = 1.0
            
            # Generate barcode image in memory without text
            buffer = BytesIO()
            code128.write(buffer, {
                'module_width': module_width,
                'module_height': module_height,
                'font_size': 0,  # Disable text in image
                'text_distance': 0,  # No space for text
                'quiet_zone': quiet_zone,
            })
            
            # Convert to base64
            buffer.seek(0)
            image_data = buffer.getvalue()
            encoded = base64.b64encode(image_data).decode('utf-8')
            buffer.close()
            
            return f"data:image/png;base64,{encoded}"
        except Exception as e:
            # Fallback to text if barcode generation fails
            return None

    def accession_number_barcode(self, obj):
        """Display accession number as a barcode image with download link."""
        barcode_data_url = self.generate_barcode_image(obj.accessionNumber)
        if barcode_data_url:
            return format_html(
                '<div style="text-align: center;">'
                '<img src="{}" alt="Barcode for {}" style="max-width: 200px; height: auto; border: 1px solid #ddd; padding: 5px; background: white; margin-bottom: 5px;" /><br/>'
                '<small style="font-family: monospace; font-size: 11px; color: #666; display: block; margin-bottom: 5px;">{}</small>'
                '<a href="{}" download="barcode_{}.png" style="font-size: 11px; color: #007bff; text-decoration: none;">Download</a>'
                '</div>',
                barcode_data_url,
                obj.accessionNumber,
                obj.accessionNumber,
                barcode_data_url,
                obj.accessionNumber
            )
        else:
            # Fallback to text only
            return format_html('<span style="font-family: monospace;">{}</span>', obj.accessionNumber)
    
    accession_number_barcode.short_description = "Accession Number"

    def approve_request(self, obj):
        """Display an approval button for book copies in 'Processing Borrow' or 'Processing Return' status."""
        if obj.status in ["Processing Borrow", "Processing Return"]:
            return format_html('<a href="/admin/approve-request/{}/" class="button">Approve</a>', obj.pk)
        return "-"

    approve_request.allow_tags = True
    approve_request.short_description = "Approve Request"

    def get_urls(self):
        """Create a custom URL for approving requests in Django admin."""
        urls = super().get_urls()
        custom_urls = [
            path("approve-request/<int:copy_id>/", self.admin_site.admin_view(self.approve_request_view), name="approve-request"),
        ]
        return custom_urls + urls

    def approve_request_view(self, request, copy_id): 
        copy_instance = get_object_or_404(BookCopy, pk=copy_id)

        if copy_instance.status == "Processing Borrow":
            copy_instance.status = "Borrowed"
        elif copy_instance.status == "Processing Return":
            copy_instance.status = "Available"
            copy_instance.borrowed_by = None
            copy_instance.student_id = None
            copy_instance.borrow_date = None
            copy_instance.return_date = None

        copy_instance.save()
        return redirect("/admin/lims_app/bookcopy/")  # Redirect after approval

# Register your models and custom admin
admin.site.register(BorrowHistory, historyAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookCopy, BookCopyAdmin)
admin.site.register(StudentActivation, StudentActivationAdmin)

# Register grade tables with bulk import
admin.site.register(grade_Seven, grade_SevenAdmin)
admin.site.register(grade_Eight, grade_EightAdmin)
admin.site.register(grade_Nine, grade_NineAdmin)
admin.site.register(grade_Ten, grade_TenAdmin)
admin.site.register(grade_Eleven, grade_ElevenAdmin)
admin.site.register(grade_Twelve, grade_TwelveAdmin)