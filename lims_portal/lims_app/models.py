from django.db import models
from django.utils import timezone
from datetime import timedelta, date
from django.core.exceptions import ValidationError

# ---------------------------------
# ACCOUNT MODEL
# ---------------------------------
GENDER_CHOICES = (
    ("Male", "Male"),
    ("Female", "Female"),
    ("Other", "Other"),
)

class grade_Seven(models.Model):
    name = models.CharField(max_length=100, unique=True,)
    school_id = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Other")
    email = models.EmailField()
    batch = models.CharField(max_length=50, null=True, blank=True, help_text="Student batch/cohort (e.g., Antuilan, Bakunawa)")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} ({self.id})"
    
class grade_Eight(models.Model):
    name = models.CharField(max_length=100, unique=True,)
    school_id = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Other")
    email = models.EmailField()
    batch = models.CharField(max_length=50, null=True, blank=True, help_text="Student batch/cohort (e.g., Antuilan, Bakunawa)")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} ({self.id})"
    
class grade_Nine(models.Model):
    name = models.CharField(max_length=100, unique=True,)
    school_id = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Other")
    email = models.EmailField()
    batch = models.CharField(max_length=50, null=True, blank=True, help_text="Student batch/cohort (e.g., Antuilan, Bakunawa)")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} ({self.id})"
    
class grade_Ten(models.Model):
    name = models.CharField(max_length=100, unique=True,)
    school_id = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Other")
    email = models.EmailField()
    batch = models.CharField(max_length=50, null=True, blank=True, help_text="Student batch/cohort (e.g., Antuilan, Bakunawa)")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} ({self.id})"
    
class grade_Eleven(models.Model):
    name = models.CharField(max_length=100, unique=True,)
    school_id = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Other")
    email = models.EmailField()
    batch = models.CharField(max_length=50, null=True, blank=True, help_text="Student batch/cohort (e.g., Antuilan, Bakunawa)")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} ({self.id})"
    
class grade_Twelve(models.Model):
    name = models.CharField(max_length=100, unique=True,)
    school_id = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Other")
    email = models.EmailField()
    batch = models.CharField(max_length=50, null=True, blank=True, help_text="Student batch/cohort (e.g., Antuilan, Bakunawa)")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} ({self.id})"
    
# ---------------------------------
# READER MODEL
# ---------------------------------
class BorrowHistory(models.Model):
    # --- User Inputs ---
    book_copy = models.ForeignKey(
        'BookCopy',
        on_delete=models.CASCADE,
        related_name='borrow_history',
        help_text="The physical book copy that was borrowed"
    )
    # Keep bookID for backward compatibility during migration
    bookID = models.CharField(
        max_length=100,
        help_text="Book Accession Number (deprecated, use book_copy)",
        blank=True,
        null=True
    )
    accountID = models.CharField(
        max_length=100,
        help_text="Enter Student School ID",
    )
    bookTitle = models.CharField(max_length=255, editable=False, blank=True)
    accountName = models.CharField(max_length=255, editable=False, blank=True)

    borrow_date = models.DateTimeField(default=timezone.now)
    return_date = models.DateTimeField(null=True, blank=True)
    returned = models.BooleanField(default=False)

    def clean(self):
        """Validate that bookID and accountID exist in their respective models."""
        from lims_app.models import Book  # adjust app name if needed
        from itertools import chain

        # --- Validate Book ---
        try:
            book = Book.objects.get(accessionNumber=self.bookID)
            self.bookTitle = book.Title
            
            # Check if book is already borrowed
            if book.status == "Borrowed" and not self.returned:
                raise ValidationError({
                    "bookID": f"Book '{self.bookID}' is already borrowed."
                })
                
        except Book.DoesNotExist:
            raise ValidationError({
                "bookID": f"No book found with accession number '{self.bookID}'."
            })
        
        # --- Validate Account (search across all grade models) ---
        account = None
        for model in [grade_Seven, grade_Eight, grade_Nine, grade_Ten, grade_Eleven, grade_Twelve]:
            try:
                account = model.objects.get(school_id=self.accountID)
                self.accountName = account.name
                break
            except model.DoesNotExist:
                continue
        
        if account is None:
            raise ValidationError({
                "accountID": f"No student found with school ID '{self.accountID}'."
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
            and self.return_date.date() < timezone.now().date()
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
    ("DOST Resources", "DOST Resources"),
    ("Journal", "Journal"),
    ("US Reference Materials", "US Reference Materials"),
    ("Other", "Other"),
)

STATUS_CHOICES = [
    ('Available', 'Available'),
    ('Unavailable', 'Unavailable'),
    ('Borrowed', 'Borrowed'),
    ('Lost', 'Lost'),
]

acquisition_STATUS = [
    ('Donated', 'Donated'),
    ('Acquired', 'Acquired'),
]

class Book(models.Model):
    Title = models.CharField(max_length=255)
    mainAuthor = models.CharField(max_length=255)
    coAuthor = models.CharField(max_length=255, null=True, blank=True)
    Publisher = models.CharField(max_length=255, null=True, blank=True)
    Edition = models.CharField(max_length=50, null=True, blank=True)
    placeofPublication = models.CharField(max_length=255, null=True, blank=True)
    copyrightDate = models.DateField(null=True, blank=True)
    publicationDate = models.DateField(null=True, blank=True)
    Editors = models.CharField(max_length=255, null=True, blank=True)
    callNumber = models.CharField(max_length=50, unique=True)
    Language = models.CharField(max_length=255)
    Type = models.CharField(max_length=50, choices=type_CHOICES, default="Other")
    acquisitionStatus = models.CharField(max_length=255, choices=acquisition_STATUS, null=True, blank=True)
    # Removed copy-specific fields: accessionNumber, status, borrowed_by, student_id, borrow_date, return_date, Location
    
    def get_total_copies(self):
        """Get total number of copies for this book"""
        return self.copies.count()
    
    def get_available_copies(self):
        """Get number of available copies"""
        return self.copies.filter(status='Available').count()
    
    def get_borrowed_copies(self):
        """Get number of borrowed copies"""
        return self.copies.filter(status='Borrowed').count()

    def __str__(self):
        return f"{self.Title} ({self.get_available_copies()}/{self.get_total_copies()} available)"


class BookCopy(models.Model):
    """Individual copy of a book with its own accession number and status"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    accessionNumber = models.CharField(max_length=50, unique=True)
    Location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    borrowed_by = models.CharField(max_length=255, null=True, blank=True)
    student_id = models.CharField(max_length=50, null=True, blank=True)
    borrow_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.book.Title} - {self.accessionNumber} ({self.status})"
    
    class Meta:
        verbose_name_plural = "Book Copies"
        ordering = ['accessionNumber']
