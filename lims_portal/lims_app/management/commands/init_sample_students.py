"""
Initialization script to create sample students for all grade levels.
Usage: python manage.py init_sample_students
"""
from django.core.management.base import BaseCommand
from lims_app.models import students
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
        
        # all the grades and their numbers, so I don't forget
        grade_levels = [
            (7, "Grade 7"),
            (8, "Grade 8"),
            (9, "Grade 9"),
            (10, "Grade 10"),
            (11, "Grade 11"),
            (12, "Grade 12"),
        ]
        
        if clear_existing:
            # nuke all the students if you want a fresh start
            students.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared all existing students\n'))
        
        # random names and stuff for fake students
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
        
        # random batch names, because why not
        batch_names = [
            "Antuilan", "Bakunawa", "Calipayan", "Dalisay", "Estrellas",
            "Fernandez", "Galura", "Himigsugan", "Ignatius", "Jaime",
            "Kasaysayan", "Lakandula", "Maharlika", "Narra", "Obrero",
            "Pagkakaisa", "Quezon", "Rizal", "Sikatuna", "Tuason"
        ]
        
        total_created = 0
        total_skipped = 0
        
        for grade_num, grade_name in grade_levels:
            self.stdout.write(f'\nCreating {count} sample students for {grade_name}...')
            
            created_count = 0
            skipped_count = 0
            
            for i in range(count):
                # make up a school ID, hope it's unique
                year = datetime.now().year
                student_num = f"{grade_num:02d}{str(i+1).zfill(3)}"
                school_id = f"PSHS{year}{student_num}"
                
                # oops, if ID exists, just add some random junk
                if students.objects.filter(school_id=school_id).exists():
                    school_id = f"PSHS{year}{student_num}X{random.randint(1,999)}"
                
                # pick a random gender and name, whatever
                gender = random.choice(["Male", "Female"])
                if gender == "Male":
                    first_name = random.choice(first_names_male)
                else:
                    first_name = random.choice(first_names_female)
                
                last_name = random.choice(last_names)
                middle_initial = random.choice(middle_initials)
                
                # name looks like: First M.I. Last (fancy)
                full_name = f"{first_name} {middle_initial} {last_name}"
                
                # make up a school email, not real
                email_base = f"{first_name.lower()}.{last_name.lower()}"
                email = f"{email_base}@pshs.edu.ph"
                
                # if name's taken, slap a number on it lol
                if students.objects.filter(name=full_name).exists():
                    # add a random number if someone already stole the name
                    suffix = random.randint(1, 999)
                    full_name = f"{first_name} {middle_initial} {last_name} {suffix}"
                
                # Assign batch - each grade gets a random batch name
                batch = random.choice(batch_names)
                
                try:
                    student = students.objects.create(
                        name=full_name,
                        school_id=school_id,
                        gender=gender,
                        email=email,
                        batch=batch,
                        grade_Level=grade_num,
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
        for grade_num, grade_name in grade_levels:
            sample_students = students.objects.filter(grade_Level=grade_num).order_by('-id')[:2]
            if sample_students:
                self.stdout.write(f'\n  {grade_name}:')
                for student in sample_students:
                    self.stdout.write(
                        f'    • {student.school_id}: {student.name} ({student.gender}) - {student.email}'
                    )
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(
                '💡 Tip: Use the admin interface to manage students!'
            )
        )
        self.stdout.write('='*60)