from django.contrib import admin
from .models import BorrowHistory, Book, grade_Seven, grade_Eight, grade_Nine, grade_Ten, grade_Eleven, grade_Twelve, StudentActivation
from django.urls import path, reverse
from django.shortcuts import redirect, get_object_or_404, render
from django.utils import timezone
from django.utils.html import format_html
from django.http import HttpResponse
from django.core.management import call_command
from django.contrib import messages
import csv
from io import StringIO

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

        # Update Book model
        try:
            book = Book.objects.get(accessionNumber=history.bookID)
            book.status = "Available"
            book.borrowed_by = None
            book.student_id = None
            book.borrow_date = None
            book.return_date = None
            book.save()
        except Book.DoesNotExist:
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
    search_fields = ['Title', 'mainAuthor', 'coAuthor', 'accessionNumber', 'Location', 'Language', 'Type']

    list_display = [
        'Title', 'mainAuthor', 'coAuthor', 'Publisher', 'placeofPublication', 'copyrightDate', 'publicationDate',
        'Editors', 'accessionNumber', 'status', 'borrow_date', 'return_date',
        'borrowed_by', 'student_id', 'approve_request'
    ]

    list_filter = ['status']  # Allow admin to filter by request type

    def approve_request(self, obj):
        """Display an approval button for books in 'Processing Borrow' or 'Processing Return' status."""
        if obj.status in ["Processing Borrow", "Processing Return"]:
            return format_html('<a href="/admin/approve-request/{}/" class="button">Approve</a>', obj.pk)
        return "-"

    approve_request.allow_tags = True
    approve_request.short_description = "Approve Request"

    def get_urls(self):
        """Create a custom URL for approving requests in Django admin."""
        urls = super().get_urls()
        custom_urls = [
            path("approve-request/<int:book_id>/", self.admin_site.admin_view(self.approve_request_view), name="approve-request"),
        ]
        return custom_urls + urls

    def approve_request_view(self, request, book_id): 
        book_instance = get_object_or_404(Book, pk=book_id)

        if book_instance.status == "Processing Borrow":
            book_instance.status = "Borrowed"
        elif book_instance.status == "Processing Return":
            book_instance.status = "Available"
            book_instance.borrowed_by = None
            book_instance.student_id = None
            book_instance.borrow_date = None
            book_instance.return_date = None

        book_instance.save()
        return redirect("/admin/library/book/")  # Redirect after approval

# Register your models and custom admin
admin.site.register(BorrowHistory, historyAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(StudentActivation, StudentActivationAdmin)

# Register grade tables with bulk import
admin.site.register(grade_Seven, grade_SevenAdmin)
admin.site.register(grade_Eight, grade_EightAdmin)
admin.site.register(grade_Nine, grade_NineAdmin)
admin.site.register(grade_Ten, grade_TenAdmin)
admin.site.register(grade_Eleven, grade_ElevenAdmin)
admin.site.register(grade_Twelve, grade_TwelveAdmin)