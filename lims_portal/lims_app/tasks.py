from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from .models import BorrowHistory, grade_Seven, grade_Eight, grade_Nine, grade_Ten, grade_Eleven, grade_Twelve
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_due_reminders_task():
    """
    Celery task to send reminders for due or overdue books.
    Scheduled to run daily at 9:00 AM via Celery Beat.
    """
    logger.info(f"[{timezone.localtime()}] Task started: send_due_reminders_task")
    
    try:
        # fetch current date
        today = timezone.localdate()
        histories = BorrowHistory.objects.filter(returned=False)
        logger.info(f"Found {histories.count()} active borrow records.")

        sent_count = 0
        failed_count = 0

        # loop for each book due
        for h in histories:
            try:
                # Search for account in all grade models
                account = None
                for model in [grade_Seven, grade_Eight, grade_Nine, grade_Ten, grade_Eleven, grade_Twelve]:
                    try:
                        account = model.objects.get(school_id=h.accountID)
                        break
                    except model.DoesNotExist:
                        continue
                
                if account is None:
                    logger.warning(f"No account found for {h.accountID}")
                    continue
            except Exception as e:
                logger.warning(f"Error finding account for {h.accountID}: {str(e)}")
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
                logger.info(f"✅ Sent reminder to {user_email}")
                sent_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to send email to {user_email}: {e}")
                failed_count += 1

        logger.info(f"Task completed: {sent_count} sent, {failed_count} failed at {timezone.localtime()}")
        return {"sent": sent_count, "failed": failed_count}

    except Exception as e:
        logger.error(f"Error in send_due_reminders_task: {e}")
        return {"error": str(e)}


@shared_task
def send_otp_email_task(email, otp, student_name):
    """
    Celery task to send OTP activation email to students.
    """
    logger.info(f"Sending OTP to {email}")
    
    subject = "Library Account Activation - OTP"
    message = (
        f"Hello {student_name},\n\n"
        f"Your account activation OTP is: {otp}\n\n"
        f"This OTP will expire in 10 minutes.\n"
        f"Do not share this code with anyone.\n\n"
        f"Thank you,\nLibrary Management System"
    )
    
    try:
        send_mail(
            subject,
            message,
            "mycarbondioxide@gmail.com",
            [email],
            fail_silently=False,
        )
        logger.info(f"✅ OTP sent to {email}")
        return {"status": "success", "email": email}
    except Exception as e:
        logger.error(f"❌ Failed to send OTP to {email}: {e}")
        return {"status": "failed", "email": email, "error": str(e)}
