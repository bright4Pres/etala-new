from django.db import models
from django.utils import timezone
from datetime import timedelta, date
from django.core.exceptions import ValidationError
import random
import string

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
    is_activated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} ({self.id})"
    
class grade_Eight(models.Model):
    name = models.CharField(max_length=100, unique=True,)
    school_id = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Other")
    email = models.EmailField()
    batch = models.CharField(max_length=50, null=True, blank=True, help_text="Student batch/cohort (e.g., Antuilan, Bakunawa)")
    is_activated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} ({self.id})"
    
class grade_Nine(models.Model):
    name = models.CharField(max_length=100, unique=True,)
    school_id = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Other")
    email = models.EmailField()
    batch = models.CharField(max_length=50, null=True, blank=True, help_text="Student batch/cohort (e.g., Antuilan, Bakunawa)")
    is_activated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} ({self.id})"
    
class grade_Ten(models.Model):
    name = models.CharField(max_length=100, unique=True,)
    school_id = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Other")
    email = models.EmailField()
    batch = models.CharField(max_length=50, null=True, blank=True, help_text="Student batch/cohort (e.g., Antuilan, Bakunawa)")
    is_activated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} ({self.id})"
    
class grade_Eleven(models.Model):
    name = models.CharField(max_length=100, unique=True,)
    school_id = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Other")
    email = models.EmailField()
    batch = models.CharField(max_length=50, null=True, blank=True, help_text="Student batch/cohort (e.g., Antuilan, Bakunawa)")
    is_activated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} ({self.id})"
    
class grade_Twelve(models.Model):
    name = models.CharField(max_length=100, unique=True,)
    school_id = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Other")
    email = models.EmailField()
    batch = models.CharField(max_length=50, null=True, blank=True, help_text="Student batch/cohort (e.g., Antuilan, Bakunawa)")
    is_activated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} ({self.id})"

class StudentActivation(models.Model):
    """Model to track OTP-based account activation for students."""
    GRADE_CHOICES = (
        (7, "Grade 7"),
        (8, "Grade 8"),
        (9, "Grade 9"),
        (10, "Grade 10"),
        (11, "Grade 11"),
        (12, "Grade 12"),
    )
    
    school_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    batch = models.CharField(max_length=4, null=True, blank=True)
    grade = models.IntegerField(choices=GRADE_CHOICES)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_activated = models.BooleanField(default=False)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def generate_otp(self):
        """Generate a random 6-digit OTP."""
        self.otp = ''.join(random.choices(string.digits, k=6))
        self.otp_created_at = timezone.now()
        self.save()
        return self.otp
    
    def verify_otp(self, entered_otp):
        """Verify if the entered OTP is correct and not expired."""
        if not self.otp_created_at:
            return False
        
        # Check if OTP is expired (10 minutes)
        expiry_time = self.otp_created_at + timedelta(minutes=10)
        if timezone.now() > expiry_time:
            return False
        
        # Check if OTP matches
        if self.otp == entered_otp:
            self.is_activated = True
            self.activated_at = timezone.now()
            self.save()
            
            # Also mark the student as activated in their grade model
            GRADE_MODELS = {
                7: grade_Seven,
                8: grade_Eight,
                9: grade_Nine,
                10: grade_Ten,
                11: grade_Eleven,
                12: grade_Twelve,
            }
            
            grade_model = GRADE_MODELS.get(self.grade)
            if grade_model:
                try:
                    student = grade_model.objects.get(school_id=self.school_id)
                    student.is_activated = True
                    student.save()
                except grade_model.DoesNotExist:
                    pass
            
            return True
        
        return False
    
    def is_otp_expired(self):
        """Check if OTP has expired."""
        if not self.otp_created_at:
            return True
        expiry_time = self.otp_created_at + timedelta(minutes=10)
        return timezone.now() > expiry_time
    
    def __str__(self):
        status = "✓ Activated" if self.is_activated else "⏳ Pending"
        return f"{self.name} ({self.school_id}) - {status}"
    
    class Meta:
        verbose_name = "Student Activation"
        verbose_name_plural = "Student Activations"
    
class ActiveStudentsManager(models.Manager):
    """Custom manager to get all students from grades 7-12."""
    def get_queryset(self):
        from itertools import chain
        from django.db.models import QuerySet
        
        # Combine all grade-level querysets
        grade_seven = grade_Seven.objects.all()
        grade_eight = grade_Eight.objects.all()
        grade_nine = grade_Nine.objects.all()
        grade_ten = grade_Ten.objects.all()
        grade_eleven = grade_Eleven.objects.all()
        grade_twelve = grade_Twelve.objects.all()
        
        # Chain all together
        all_students = list(chain(
            grade_seven, grade_eight, grade_nine,
            grade_ten, grade_eleven, grade_twelve
        ))
        return all_students

class activeStudents(models.Model):
    name = models.CharField(max_length=100, unique=True,)
    school_id = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Other")
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = ActiveStudentsManager()
    class Meta:
        managed = False  # Don't create a separate table
    
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
        
        # --- Check if student is activated ---
        if not account.is_activated:
            raise ValidationError({
                "accountID": f"Student '{account.name}' has not been activated yet. Please complete OTP verification to borrow books."
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
    accessionNumber = models.CharField(max_length=50, unique=True)
    callNumber = models.CharField(max_length=50, unique=True)
    Location = models.CharField(max_length=255)
    Language = models.CharField(max_length=255)
    Type = models.CharField(max_length=50, choices=type_CHOICES, default="Other")
    borrowed_by = models.CharField(max_length=255, null=True, blank=True)
    student_id = models.CharField(max_length=50, null=True, blank=True)
    borrow_date = models.DateField(null=True, blank=True)
    acquisitionStatus = models.CharField(max_length=255, choices=acquisition_STATUS, null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')

    def __str__(self):
        return self.Title