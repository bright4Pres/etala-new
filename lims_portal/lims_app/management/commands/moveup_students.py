"""
Management command to move students up to the next grade level.
Usage: python manage.py moveup_students
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from lims_app.models import (
    grade_Seven, grade_Eight, grade_Nine, 
    grade_Ten, grade_Eleven, grade_Twelve,
    StudentActivation
)


class Command(BaseCommand):
    help = 'Move all students up to the next grade level (Grade 7→8, 8→9, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without applying them',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved\n'))
        
        # Grade progression mapping
        grade_progression = [
            (grade_Eleven, grade_Twelve, 11, 12, 'Grade 11', 'Grade 12'),
            (grade_Ten, grade_Eleven, 10, 11, 'Grade 10', 'Grade 11'),
            (grade_Nine, grade_Ten, 9, 10, 'Grade 9', 'Grade 10'),
            (grade_Eight, grade_Nine, 8, 9, 'Grade 8', 'Grade 9'),
            (grade_Seven, grade_Eight, 7, 8, 'Grade 7', 'Grade 8'),
        ]
        
        # Statistics
        total_moved = 0
        total_graduated = 0
        errors = []
        
        with transaction.atomic():
            # Process from highest grade to lowest to avoid conflicts
            for source_model, target_model, source_grade, target_grade, source_name, target_name in grade_progression:
                students = source_model.objects.all()
                moved_count = 0
                
                self.stdout.write(f'\n{source_name} → {target_name}:')
                
                for student in students:
                    try:
                        # Check if student with same school_id already exists in target
                        if target_model.objects.filter(school_id=student.school_id).exists():
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  ⚠ Skipped {student.name} ({student.school_id}) - already exists in {target_name}'
                                )
                            )
                            continue
                        
                        # Create in target grade
                        target_model.objects.create(
                            name=student.name,
                            school_id=student.school_id,
                            gender=student.gender,
                            email=student.email,
                            is_activated=student.is_activated,
                            created_at=student.created_at
                        )
                        
                        # Update StudentActivation record if exists
                        try:
                            activation = StudentActivation.objects.get(school_id=student.school_id)
                            activation.grade = target_grade
                            activation.save()
                        except StudentActivation.DoesNotExist:
                            pass
                        
                        # Delete from source grade
                        if not dry_run:
                            student.delete()
                        
                        moved_count += 1
                        total_moved += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ Moved {student.name} ({student.school_id})'
                            )
                        )
                        
                    except Exception as e:
                        error_msg = f'Error moving {student.name} ({student.school_id}): {str(e)}'
                        errors.append(error_msg)
                        self.stdout.write(self.style.ERROR(f'  ✗ {error_msg}'))
                
                self.stdout.write(f'  Total moved: {moved_count}')
            
            # Handle Grade 12 graduations
            grade_12_students = grade_Twelve.objects.all()
            graduated_count = 0
            
            if grade_12_students.exists():
                self.stdout.write(f'\n\nGrade 12 → Graduated:')
                for student in grade_12_students:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  🎓 {student.name} ({student.school_id}) will be removed (graduated)'
                        )
                    )
                    graduated_count += 1
                    total_graduated += 1
                    
                    # Delete StudentActivation record for graduated students
                    try:
                        activation = StudentActivation.objects.get(school_id=student.school_id)
                        if not dry_run:
                            activation.delete()
                    except StudentActivation.DoesNotExist:
                        pass
                    
                    if not dry_run:
                        student.delete()
                
                self.stdout.write(f'  Total graduated: {graduated_count}')
            
            # Rollback if dry run
            if dry_run:
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING('\n\nDRY RUN COMPLETE - No changes were saved'))
            else:
                self.stdout.write(self.style.SUCCESS('\n\n✅ Move-up complete!'))
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('SUMMARY:')
        self.stdout.write(f'  Students moved up: {total_moved}')
        self.stdout.write(f'  Students graduated (removed): {total_graduated}')
        self.stdout.write(f'  Errors: {len(errors)}')
        
        if errors:
            self.stdout.write('\nERRORS:')
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  • {error}'))
        
        self.stdout.write('='*50)
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n✅ All students have been moved up successfully!'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'Note: Grade 12 students have been removed (graduated).'
                )
            )
