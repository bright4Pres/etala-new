from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from lims_app.models import BorrowHistory, Account
import time


class Command(BaseCommand):
    help = "Send reminders for due or overdue books at 9:00 AM daily."

    def handle(self, *args, **kwargs):
        # start time
        self.stdout.write(self.style.NOTICE(f"[{timezone.localtime()}] Command started."))

        # target time
        now = timezone.localtime()
        target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)

        # function to wait until target time
        if now < target_time:
            wait_seconds = (target_time - now).total_seconds()
            wait_minutes = wait_seconds / 60
            wait_hours = wait_minutes / 60
            self.stdout.write(f"Waiting {wait_hours:.0f} hours or {wait_minutes:.0f} minutes or {wait_seconds:.0f} seconds until 9:00 AM")
            time.sleep(wait_seconds)

        # fetch current date
        today = timezone.localdate()
        histories = BorrowHistory.objects.filter(returned=False)
        self.stdout.write(self.style.NOTICE(f"Found {histories.count()} active borrow records."))

        # loop for each book due
        for h in histories:
            try:
                account = Account.objects.get(school_id=h.accountID)
            except Account.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"No account found for {h.accountID}"))
                continue

            return_date = h.return_date.date() if hasattr(h.return_date, "date") else h.return_date

            user_email = account.email
            name = h.accountName
            book_title = h.bookTitle
            book_id = h.bookID

            # determine if due today or overdue
            if return_date == today:
                subject = f"Reminder: Book '{book_title}' is due today"
                message = (
                    f"Hello {name},\n\n"
                    f"The book '{book_title}' (ID: {book_id}) is due today ({today}). "
                    f"Please return it on time to avoid penalties.\n\n"
                    f"Thank you,\nLibrary Management System"
                )
            elif return_date < today:
                overdue_days = (today - return_date).days
                subject = f"Overdue Notice: Book '{book_title}'"
                message = (
                    f"Hello {name},\n\n"
                    f"The book '{book_title}' (ID: {book_id}) was due on {return_date} "
                    f"and is now {overdue_days} day(s) overdue.\n"
                    f"Please return it as soon as possible.\n\n"
                    f"Thank you,\nLibrary Management System"
                )
            else:
                continue  # Not due yet

            # send email
            try:
                send_mail(
                    subject,
                    message,
                    "mycarbondioxide@gmail.com", 
                    [user_email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f"✅ Sent reminder to {user_email}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Failed to send email to {user_email}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Reminders finished at {timezone.localtime()}"))