"""
Management command to move students up to the next grade level.
Usage: python manage.py moveup_students
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from lims_app.models import students


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
        
        # ok so like, this is how grades move up (pls don't mess up order)
        grade_progression = [
            (11, 12, 'Grade 11', 'Grade 12'),
            (10, 11, 'Grade 10', 'Grade 11'),
            (9, 10, 'Grade 9', 'Grade 10'),
            (8, 9, 'Grade 8', 'Grade 9'),
            (7, 8, 'Grade 7', 'Grade 8'),
        ]
        
        # keeping score for how many kids move up n stuff
        total_moved = 0
        total_graduated = 0
        errors = []
        
        with transaction.atomic():
            # grab the seniors first so they don't get caught in the move-up
            graduating_students = list(students.objects.filter(grade_Level=12))

            # do the top grades first so we don't mess up order
            for source_grade, target_grade, source_name, target_name in grade_progression:
                grade_students = students.objects.filter(grade_Level=source_grade)
                moved_count = 0

                self.stdout.write(f'\n{source_name} -> {target_name}:')

                for student in grade_students:
                    try:
                        if not dry_run:
                            student.grade_Level = target_grade
                            student.save(update_fields=['grade_Level'])

                        moved_count += 1
                        total_moved += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  -> Moved {student.name} ({student.school_id})'
                            )
                        )
                    except Exception as e:
                        error_msg = f'Error moving {student.name} ({student.school_id}): {str(e)}'
                        errors.append(error_msg)
                        self.stdout.write(self.style.ERROR(f'  !! {error_msg}'))

                self.stdout.write(f'  Total moved: {moved_count}')

            # ok, now the Grade 12s are outta here (bye seniors)
            graduated_count = 0

            if graduating_students:
                self.stdout.write(f'\n\nGrade 12 -> Graduated:')
                for student in graduating_students:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  -> {student.name} ({student.school_id}) will be removed (graduated)'
                        )
                    )
                    graduated_count += 1
                    total_graduated += 1

                    if not dry_run:
                        student.delete()

                self.stdout.write(f'  Total graduated: {graduated_count}')

            # if we're just pretending, undo everything lol
            if dry_run:
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING('\n\nDRY RUN COMPLETE - No changes were saved'))
            else:
                self.stdout.write(self.style.SUCCESS('\n\nMove-up complete!'))
        
        # tldr for lazy people
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
