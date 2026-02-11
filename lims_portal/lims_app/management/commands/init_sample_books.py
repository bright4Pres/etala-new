"""
Initialization script to create 100 sample books for testing.
Usage: python manage.py init_sample_books
"""
from django.core.management.base import BaseCommand
from lims_app.models import Book
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Create 100 sample books for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Number of sample books to create (default: 100)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing books before creating samples',
        )

    def handle(self, *args, **options):
        count = options['count']
        clear_existing = options['clear']
        
        if clear_existing:
            Book.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared all existing books\n'))
        
        # Sample data
        book_titles = [
            "Introduction to Physics", "Advanced Mathematics", "Chemistry Fundamentals",
            "Biology Essentials", "World History", "Philippine Literature",
            "English Grammar", "Computer Science Basics", "Statistics and Probability",
            "Creative Writing", "Philosophy 101", "Psychology Today",
            "Economics Principles", "Political Science", "Sociology Basics",
            "Calculus I", "Geometry", "Algebra II",
            "Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry",
            "Cell Biology", "Genetics", "Ecology and Environment",
            "Modern Physics", "Quantum Mechanics", "Thermodynamics",
            "Data Structures", "Algorithms", "Database Systems",
            "Web Development", "Machine Learning", "Artificial Intelligence",
            "Filipino Panitikan", "Noli Me Tangere", "El Filibusterismo",
            "Rizal's Life and Works", "Asian History", "European History",
            "American Literature", "British Literature", "Poetry Anthology",
            "Short Stories Collection", "Novel Writing", "Research Methods",
            "Thesis Writing", "Academic Writing", "Scientific Method",
            "Laboratory Techniques", "Experimental Design", "Data Analysis",
            "Critical Thinking", "Logic and Reasoning", "Ethics",
        ]
        
        authors_first = [
            "Maria", "Juan", "Jose", "Ana", "Carlos", "Sofia", 
            "Miguel", "Isabel", "Antonio", "Carmen", "Pedro", "Rosa",
            "Gabriel", "Elena", "Rafael", "Lucia", "Fernando", "Teresa",
            "Manuel", "Beatriz", "Ricardo", "Clara", "Diego", "Victoria"
        ]
        
        authors_last = [
            "Santos", "Garcia", "Cruz", "Reyes", "Ramos", "Flores",
            "Gonzales", "Torres", "Rivera", "Martinez", "Hernandez", "Lopez",
            "Perez", "Rodriguez", "Sanchez", "Ramirez", "Castillo", "Morales",
            "Jimenez", "Romero", "Gutierrez", "Alvarez", "Mendoza", "Vargas"
        ]
        
        publishers = [
            "Rex Bookstore", "National Book Store", "Anvil Publishing",
            "Ateneo de Manila University Press", "University of the Philippines Press",
            "Pearson Education", "McGraw-Hill", "Oxford University Press",
            "Cambridge University Press", "Cengage Learning", "Vibal Group",
            "Phoenix Publishing", "Goodwill Bookstore", "C&E Publishing"
        ]
        
        locations = [
            "Science Section - Shelf A1", "Science Section - Shelf A2",
            "Science Section - Shelf B1", "Science Section - Shelf B2",
            "Math Section - Shelf C1", "Math Section - Shelf C2",
            "Literature Section - Shelf D1", "Literature Section - Shelf D2",
            "Social Studies - Shelf E1", "Social Studies - Shelf E2",
            "Computer Science - Shelf F1", "Computer Science - Shelf F2",
            "Filipino Section - Shelf G1", "Filipino Section - Shelf G2",
            "Reference Section - Shelf H1", "Reference Section - Shelf H2"
        ]
        
        languages = ["English", "Filipino", "Spanish", "French"]
        book_types = ["Books", "Analytics", "Article", "Thesis"]
        
        self.stdout.write(f'Creating {count} sample books...\n')
        
        created_count = 0
        skipped_count = 0
        
        for i in range(count):
            # Generate unique accession number
            year = random.randint(2015, 2025)
            accession_num = f"BK{year}-{str(i+1).zfill(5)}"
            
            # Check if accession number already exists
            if Book.objects.filter(accessionNumber=accession_num).exists():
                accession_num = f"BK{year}-{str(random.randint(10000, 99999))}"
            
            # Random book details
            title_base = random.choice(book_titles)
            volume = random.choice(["", " Vol. I", " Vol. II", " Vol. III", ""])
            edition_suffix = random.choice(["", " (2nd Edition)", " (3rd Edition)", " (Revised Edition)", ""])
            title = f"{title_base}{volume}{edition_suffix}"
            
            # Edition field (separate from title)
            edition = random.choice([
                "1st Edition", "2nd Edition", "3rd Edition", "4th Edition", 
                "Revised Edition", "Special Edition", None
            ])
            
            author_first = random.choice(authors_first)
            author_last = random.choice(authors_last)
            main_author = f"{author_first} {author_last}"
            
            # Generate call number (Library classification)
            # Format: Dewey Decimal-like or Library of Congress-like
            call_prefix = random.choice([
                "QC", "QD", "QH", "QA", "PE", "PL", "HT", "HD", "LB", "Z",  # LC style
                "500", "540", "570", "510", "420", "800", "300", "370", "000"  # Dewey style
            ])
            call_year = str(random.randint(2000, 2025))[-2:]
            call_suffix = random.choice(["A", "B", "C", "D", "E", "F", "G", "H"])
            call_number = f"{call_prefix}{random.randint(1, 999)}.{call_suffix}{call_year}"
            
            # Ensure call_number is unique
            attempt = 0
            while Book.objects.filter(callNumber=call_number).exists() and attempt < 10:
                call_number = f"{call_prefix}{random.randint(1, 999)}.{call_suffix}{random.randint(10, 99)}"
                attempt += 1
            
            # Sometimes add co-author
            co_author = None
            if random.random() > 0.6:
                co_first = random.choice(authors_first)
                co_last = random.choice(authors_last)
                co_author = f"{co_first} {co_last}"
            
            publisher = random.choice(publishers)
            location = random.choice(locations)
            language = random.choice(languages)
            book_type = random.choice(book_types)
            
            # Random dates
            copyright_year = random.randint(2000, 2024)
            copyright_date = datetime(copyright_year, random.randint(1, 12), random.randint(1, 28))
            publication_date = copyright_date + timedelta(days=random.randint(0, 365))
            
            # Create book
            try:
                Book.objects.create(
                    Title=title,
                    mainAuthor=main_author,
                    coAuthor=co_author,
                    Publisher=publisher,
                    Edition=edition,
                    placeofPublication=random.choice(["Manila", "Quezon City", "Makati", "Cebu City", "Davao City"]),
                    copyrightDate=copyright_date.date(),
                    publicationDate=publication_date.date(),
                    Editors=f"Editorial Board of {publisher}" if random.random() > 0.7 else None,
                    accessionNumber=accession_num,
                    callNumber=call_number,
                    Location=location,
                    Language=language,
                    Type=book_type,
                    status='Available'
                )
                created_count += 1
                
                if (created_count) % 10 == 0:
                    self.stdout.write(f'  Created {created_count} books...')
                    
            except Exception as e:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f'  Skipped book {i+1}: {str(e)}')
                )
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Successfully created {created_count} sample books!'
            )
        )
        if skipped_count > 0:
            self.stdout.write(
                self.style.WARNING(f'⚠ Skipped {skipped_count} books due to errors')
            )
        self.stdout.write('='*50)
        
        # Display some sample books
        self.stdout.write('\nSample of created books:')
        sample_books = Book.objects.order_by('-id')[:5]
        for book in sample_books:
            edition_text = f" - {book.Edition}" if book.Edition else ""
            self.stdout.write(
                f'  • [{book.callNumber}] {book.accessionNumber}: {book.Title}{edition_text} by {book.mainAuthor} ({book.Type})'
            )
