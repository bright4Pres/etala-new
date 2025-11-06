from django.contrib import admin
from .models import BorrowHistory, Book, Account
from django.urls import path, reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect, get_object_or_404

class CirculationAdmin(admin.ModelAdmin):
    change_list_template = "admin/circulation_change_list.html"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset

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
    
class AccountAdmin(admin.ModelAdmin):
    search_fields = ['name', 'email', 'school_id', 'batch', 'created_at']
    list_display = ['name', 'email', 'school_id']

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
admin.site.register(Account, AccountAdmin)