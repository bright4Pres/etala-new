from django.db import models
from django.utils import timezone
from datetime import timedelta, date
from django.core.exceptions import ValidationError

# ---------------------------------
# ACCOUNT MODEL
# ---------------------------------
class Account(models.Model):
    name = models.CharField(max_length=100, unique=True,)
    school_id = models.CharField(max_length=50, unique=True)
    batch = models.TextField(max_length=4, default="e.g. 2026")
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} ({self.id})"

# ---------------------------------
# READER MODEL
# ---------------------------------
class BorrowHistory(models.Model):
    # --- User Inputs ---
    bookID = models.CharField(
        max_length=100,
        help_text="Enter Book Accession Number",
    )
    accountID = models.CharField(
        max_length=100,
        help_text="Enter Student School ID",
    )

    # --- Auto-Filled (uneditable) Fields ---
    bookTitle = models.CharField(max_length=255, editable=False, blank=True)
    accountName = models.CharField(max_length=255, editable=False, blank=True)

    borrow_date = models.DateTimeField(default=timezone.now)
    return_date = models.DateTimeField(null=True, blank=True)
    returned = models.BooleanField(default=False)

    def clean(self):
        """Validate that bookID and accountID exist in their respective models."""
        from lims_app.models import Book, Account  # adjust app name if needed

        # --- Validate Book ---
        try:
            book = Book.objects.get(accessionNumber=self.bookID)
            self.bookTitle = book.Title
        except Book.DoesNotExist:
            raise ValidationError({
                "bookID": f"No book found with accession number '{self.bookID}'."
            })

        # --- Validate Account ---
        try:
            account = Account.objects.get(school_id=self.accountID)
            self.accountName = account.name
        except Account.DoesNotExist:
            raise ValidationError({
                "accountID": f"No account found with school ID '{self.accountID}'."
            })

    def save(self, *args, **kwargs):
        """Auto-fill fields, validate, and compute return date."""
        self.full_clean()  # Ensures clean() runs every time before save()

        # --- Compute return date if missing ---
        if self.borrow_date and not self.return_date:
            proposed_return = self.borrow_date + timedelta(days=1)

            # If borrowed on Friday, move return date to Wednesday
            if self.borrow_date.weekday() == 4:  # Friday
                proposed_return += timedelta(days=4)

            # If proposed return is weekend, shift to Monday
            if proposed_return.weekday() == 5:  # Saturday
                proposed_return += timedelta(days=2)
            elif proposed_return.weekday() == 6:  # Sunday
                proposed_return += timedelta(days=1)

            self.return_date = proposed_return

        # --- Update Book record when borrowed ---
        from lims_app.models import Book
        try:
            book = Book.objects.get(accessionNumber=self.bookID)
            book.status = "Borrowed"
            book.borrowed_by = self.accountName
            book.student_id = self.accountID
            book.borrow_date = self.borrow_date
            book.return_date = self.return_date
            book.save()
        except Book.DoesNotExist:
            # The ValidationError in clean() already handles this, so this won't normally happen
            pass

        super().save(*args, **kwargs)

    def is_overdue(self):
        """Check if this borrow record is overdue."""
        return (
            not self.returned
            and self.return_date
            and self.return_date < timezone.now().date()
        )

    def __str__(self):
        return f"{self.accountName or self.accountID} borrowed {self.bookTitle or self.bookID}"
# ---------------------------------
# BOOK MODEL
# ---------------------------------
type_CHOICES = (
    ("Analytics", "Analytics"),
    ("Article", "Article"),
    ("Books", "Books"),
    ("Thesis", "Thesis"),
)

STATUS_CHOICES = [
    ('Available', 'Available'),
    ('Borrowed', 'Borrowed'),
]


class Book(models.Model):
    Title = models.CharField(max_length=255)
    mainAuthor = models.CharField(max_length=255)
    coAuthor = models.CharField(max_length=255, null=True, blank=True)
    Publisher = models.CharField(max_length=255, null=True, blank=True)
    placeofPublication = models.CharField(max_length=255, null=True, blank=True)
    copyrightDate = models.DateField(null=True, blank=True)
    publicationDate = models.DateField(null=True, blank=True)
    Editors = models.CharField(max_length=255, null=True, blank=True)
    accessionNumber = models.CharField(max_length=50, unique=True)
    Location = models.CharField(max_length=255)
    Language = models.CharField(max_length=255)
    Type = models.CharField(max_length=50, choices=type_CHOICES, default="Other")
    borrowed_by = models.CharField(max_length=255, null=True, blank=True)
    student_id = models.CharField(max_length=50, null=True, blank=True)
    borrow_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')

    def __str__(self):
        return self.Title