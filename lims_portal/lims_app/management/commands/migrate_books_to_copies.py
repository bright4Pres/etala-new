"""
Data migration script to convert existing flat Book records to Book + BookCopy structure.
This script handles the transition from the old single-table model to the new two-table model.

Usage: python manage.py migrate_books_to_copies
"""
from django.core.management.base import BaseCommand
from lims_app.models import Book, BookCopy, BorrowHistory
from django.db import transaction


class Command(BaseCommand):
    help = 'Migrate existing Book records to Book + BookCopy structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made\n'))
        
        # Note: This migration assumes the old Book model had accessionNumber, status, Location fields
        # which have been removed in the new structure
        
        self.stdout.write('Analyzing existing data...\n')
        
        # Since we've already migrated the model, we need to check if there are any
        # Book records without associated BookCopy records
        books_without_copies = Book.objects.filter(copies__isnull=True)
        
        if books_without_copies.count() == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ All books already have copies. No migration needed.')
            )
            return
        
        self.stdout.write(f'Found {books_without_copies.count()} books without copies\n')
        
        if not dry_run:
            with transaction.atomic():
                migrated_count = 0
                error_count = 0
                
                for book in books_without_copies:
                    try:
                        # Create a default BookCopy for each book without copies
                        # Generate a default accession number based on book ID
                        accession_num = f"LEG-{book.id:06d}"
                        
                        # Check if this accession number already exists
                        if BookCopy.objects.filter(accessionNumber=accession_num).exists():
                            accession_num = f"LEG-{book.id:06d}-{book.mainAuthor[:3].upper()}"
                        
                        BookCopy.objects.create(
                            book=book,
                            accessionNumber=accession_num,
                            Location="Legacy Collection",  # Default location
                            status='Available'
                        )
                        
                        migrated_count += 1
                        
                        if migrated_count % 10 == 0:
                            self.stdout.write(f'  Migrated {migrated_count} books...')
                        
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'  Error migrating book {book.id}: {str(e)}')
                        )
                
                self.stdout.write('\n' + '='*60)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Successfully migrated {migrated_count} books to Book+BookCopy structure'
                    )
                )
                if error_count > 0:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ {error_count} errors encountered')
                    )
                self.stdout.write('='*60)
        else:
            self.stdout.write('\nDry run complete. Use without --dry-run to apply changes.')
        
        # Report on BorrowHistory records that may need updating
        self.stdout.write('\nChecking BorrowHistory records...')
        history_without_copy = BorrowHistory.objects.filter(book_copy__isnull=True)
        
        if history_without_copy.count() > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠ Found {history_without_copy.count()} BorrowHistory records without book_copy reference'
                )
            )
            self.stdout.write(
                '  These records have bookID (accession number) but need to be linked to BookCopy.'
            )
            self.stdout.write(
                '  Run: python manage.py link_borrow_history  (to be created)'
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ All BorrowHistory records properly linked')
            )
