from django.db import models
from django.utils import timezone
from datetime import timedelta, date

# ---------------------------------
# ACCOUNT MODEL
# ---------------------------------
class account(models.Model):
    account_name = models.CharField(max_length=100, unique=True, default="Bright Bastasa")
    account_id = models.CharField(max_length=50, unique=True, default="13-2020-052")
    account_address = models.TextField(default="e.g. example@gmail.com")
    account_batch = models.TextField(max_length=4, default="e.g. 2026")

    def __str__(self):
        return self.account_name


# ---------------------------------
# READER MODEL
# ---------------------------------
class reader(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    reader_name = models.CharField(max_length=200)
    reader_id = models.CharField(max_length=200)
    reader_contact = models.CharField(max_length=200)
    reader_address = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    borrowDate = models.DateField(default=timezone.now)
    returnDate = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.borrowDate and not self.returnDate:
            self.returnDate = self.borrowDate + timedelta(weeks=1)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.reader_name


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
    ('Processing Borrow', 'Processing Borrow'),
    ('Processing Return', 'Processing Return'),
    ('Borrowed', 'Borrowed'),
]


class book(models.Model):
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