"""
Initialization script to create sample students for all grade levels.
Usage: python manage.py init_sample_students
"""
from django.core.management.base import BaseCommand
from lims_app.models import grade_Seven, grade_Eight, grade_Nine, grade_Ten, grade_Eleven, grade_Twelve
from datetime import datetime
import random


class Command(BaseCommand):
    help = 'Create sample students for all grade levels'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=30,
            help='Number of sample students per grade level (default: 30)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing students before creating samples',
        )

    def handle(self, *args, **options):
        count = options['count']
        clear_existing = options['clear']
        
        # Grade models and their corresponding StudentActivation grade numbers
        grade_models = [
            (grade_Seven, 7, "Grade 7"),
            (grade_Eight, 8, "Grade 8"),
            (grade_Nine, 9, "Grade 9"),
            (grade_Ten, 10, "Grade 10"),
            (grade_Eleven, 11, "Grade 11"),
            (grade_Twelve, 12, "Grade 12"),
        ]
        
        if clear_existing:
            # Clear all grade tables
            for model, _, _ in grade_models:
                model.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared all existing students\n'))
        
        # Sample data
        first_names_male = [
            "Juan", "Pedro", "Jose", "Miguel", "Antonio", "Carlos", "Luis", "Fernando",
            "Ricardo", "Roberto", "Eduardo", "Rafael", "Gabriel", "Manuel", "Francisco",
            "Alberto", "Diego", "Alejandro", "Sergio", "Pablo", "Mario", "Jorge", "Ruben",
            "Victor", "Oscar", "Adrian", "Enrique", "Salvador", "Angel", "Guillermo"
        ]
        
        first_names_female = [
            "Maria", "Ana", "Rosa", "Carmen", "Isabel", "Teresa", "Pilar", "Dolores",
            "Cristina", "Laura", "Patricia", "Mercedes", "Concepcion", "Lucia", "Elena",
            "Sofia", "Victoria", "Angela", "Beatriz", "Silvia", "Monica", "Pilar",
            "Julia", "Paula", "Raquel", "Andrea", "Sara", "Claudia", "Natalia", "Eva"
        ]
        
        last_names = [
            "Santos", "Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
            "Perez", "Sanchez", "Ramirez", "Torres", "Flores", "Rivera", "Gomez", "Diaz",
            "Morales", "Ortiz", "Gutierrez", "Chavez", "Ramos", "Hernandez", "Jimenez",
            "Ruiz", "Fernandez", "Moreno", "Alvarez", "Romero", "Navarro", "Vargas",
            "Castillo", "Guerrero", "Cortes", "Mendoza", "Delgado", "Aguilar", "Medina",
            "Dominguez", "Silva", "Morales", "Rojas", "Ortega", "Santiago", "Luna"
        ]
        
        middle_initials = ["A.", "B.", "C.", "D.", "E.", "F.", "G.", "H.", "I.", "J."]
        
        # Sample batch names (PSHS-ZRC traditional batch names)
        batch_names = [
            "Antuilan", "Bakunawa", "Calipayan", "Dalisay", "Estrellas",
            "Fernandez", "Galura", "Himigsugan", "Ignatius", "Jaime",
            "Kasaysayan", "Lakandula", "Maharlika", "Narra", "Obrero",
            "Pagkakaisa", "Quezon", "Rizal", "Sikatuna", "Tuason"
        ]
        
        total_created = 0
        total_skipped = 0
        
        for model, grade_num, grade_name in grade_models:
            self.stdout.write(f'\nCreating {count} sample students for {grade_name}...')
            
            created_count = 0
            skipped_count = 0
            
            for i in range(count):
                # Generate unique school ID
                year = datetime.now().year
                student_num = f"{grade_num:02d}{str(i+1).zfill(3)}"
                school_id = f"PSHS{year}{student_num}"
                
                # Check if school_id already exists
                if model.objects.filter(school_id=school_id).exists():
                    school_id = f"PSHS{year}{student_num}X{random.randint(1,999)}"
                
                # Random gender and name generation
                gender = random.choice(["Male", "Female"])
                if gender == "Male":
                    first_name = random.choice(first_names_male)
                else:
                    first_name = random.choice(first_names_female)
                
                last_name = random.choice(last_names)
                middle_initial = random.choice(middle_initials)
                
                # Full name format: First M.I. Last
                full_name = f"{first_name} {middle_initial} {last_name}"
                
                # Generate email
                email_base = f"{first_name.lower()}.{last_name.lower()}"
                email = f"{email_base}@pshs.edu.ph"
                
                # Check for name uniqueness (since name field is unique)
                if model.objects.filter(name=full_name).exists():
                    # Add suffix if name exists
                    suffix = random.randint(1, 999)
                    full_name = f"{first_name} {middle_initial} {last_name} {suffix}"
                
                # Assign batch - each grade gets a random batch name
                batch = random.choice(batch_names)
                
                try:
                    student = model.objects.create(
                        name=full_name,
                        school_id=school_id,
                        gender=gender,
                        email=email,
                        batch=batch,
                        is_activated=False  # Start as not activated
                    )
                    created_count += 1
                    
                    if (created_count) % 10 == 0:
                        self.stdout.write(f'  Created {created_count} students for {grade_name}...')
                        
                except Exception as e:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'  Skipped student {i+1} for {grade_name}: {str(e)}')
                    )
            
            total_created += created_count
            total_skipped += skipped_count
            
            self.stdout.write(
                self.style.SUCCESS(f'  ✅ {grade_name}: {created_count} created, {skipped_count} skipped')
            )
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(
                f'🎓 Successfully created {total_created} sample students!'
            )
        )
        if total_skipped > 0:
            self.stdout.write(
                self.style.WARNING(f'⚠ Skipped {total_skipped} students due to errors')
            )
        self.stdout.write('='*60)
        
        # Display sample students from each grade
        self.stdout.write('\nSample students created:')
        for model, grade_num, grade_name in grade_models:
            sample_students = model.objects.filter(is_activated=False).order_by('-id')[:2]
            if sample_students:
                self.stdout.write(f'\n  {grade_name}:')
                for student in sample_students:
                    self.stdout.write(
                        f'    • {student.school_id}: {student.name} ({student.gender}) - {student.email}'
                    )
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(
                '💡 Tip: Students start as "not activated". Use the admin interface to activate them!'
            )
        )
        self.stdout.write('='*60)