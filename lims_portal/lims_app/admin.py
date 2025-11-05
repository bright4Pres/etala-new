from django.contrib import admin
from .models import reader, book, account
from django.utils import timezone
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect, get_object_or_404

class CirculationAdmin(admin.ModelAdmin):
    change_list_template = "admin/circulation_change_list.html"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset

class ReaderAdmin(admin.ModelAdmin):
    search_fields = ['id', 'reader_name', 'reader_id', 'reader_contact', 'reader_address', 'name']
    list_display = ['id', 'reader_name', 'reader_id', 'reader_contact', 'reader_address', 'name',
                    'borrowDate', 'returnDate', 'active']
    list_filter = ['borrowDate', 'returnDate', 'active']
    ordering = ['returnDate']


class AccountAdmin(admin.ModelAdmin):
    search_fields = ['account_name', 'account_address', 'account_id', 'account_batch']
    list_display = ['account_name', 'account_address', 'account_id']

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
        book_instance = get_object_or_404(book, pk=book_id)

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
admin.site.register(reader, ReaderAdmin)
admin.site.register(book, BookAdmin)
admin.site.register(account, AccountAdmin)