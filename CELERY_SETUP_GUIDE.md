# LIMS Portal - Setup Guide for Celery & OTP

## 1. Install Required Packages

```bash
pip install celery redis
```

Or if you prefer RabbitMQ:
```bash
pip install celery
# Then install RabbitMQ separately (depending on OS)
```

## 2. Configure Django Settings (settings.py)

Add these settings to your Django settings.py:

```python
# ============ CELERY CONFIGURATION ============
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # For Redis
# CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'  # For RabbitMQ

CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # For Redis
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Celery Task Configuration
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

# ============ EMAIL CONFIGURATION ============
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use App Password, not regular password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

## 3. Start Redis (if using Redis as broker)

```bash
# On Windows (with WSL or native Redis)
redis-server

# On macOS
brew services start redis

# On Linux
sudo systemctl start redis
```

## 4. Run Celery Worker

```bash
# Basic worker
celery -A lims_portal worker -l info

# With auto-reload on code changes
celery -A lims_portal worker -l info --autoscale=10,3
```

## 5. Run Celery Beat (Scheduler)

In a new terminal:
```bash
celery -A lims_portal beat -l info
```

## 6. Database Migration

After updating models with StudentActivation:

```bash
python manage.py makemigrations
python manage.py migrate
```

## 7. Admin Features

### CSV Import for Students
- Go to Admin → Grade 7/8/9/10/11/12
- Click "Import CSV"
- Download template or upload your CSV

### Student Activation Management
- Go to Admin → Student Activations
- View all pending and activated students
- Click "Resend OTP" to send activation code to student

## 8. OTP Workflow

### Student Activation Flow:
1. **Admin imports student CSV** → Student record created in StudentActivation
2. **OTP is generated** (6 digits, expires in 10 minutes)
3. **OTP sent to student email** (via Celery task)
4. **Student enters OTP** to activate account
5. **Account activated** → Student can now borrow books

### Generate OTP (in code or shell):
```python
from lims_app.models import StudentActivation
from lims_app.tasks import send_otp_email_task

# Get or create student activation
activation = StudentActivation.objects.get(school_id='S12345')

# Generate OTP
otp = activation.generate_otp()

# Send via Celery (async)
send_otp_email_task.delay(activation.email, otp, activation.name)

# Or send immediately (sync)
send_otp_email_task(activation.email, otp, activation.name)
```

### Verify OTP:
```python
activation = StudentActivation.objects.get(school_id='S12345')
is_valid = activation.verify_otp('123456')  # Returns True/False
```

## 9. Scheduled Tasks

### Daily Reminder at 9:00 AM
Automatically sends overdue/due book reminders to students every day at 9:00 AM.

**Task:** `send_due_reminders_task` (defined in tasks.py)
**Schedule:** Runs daily at 9:00 AM UTC

### Email OTP
Sends OTP emails asynchronously without blocking the server.

**Task:** `send_otp_email_task`

## 10. Monitoring & Debugging

### Check Celery tasks status:
```python
from celery.result import AsyncResult

# Get task result
task_id = 'xxx-xxx-xxx'
result = AsyncResult(task_id)
print(result.state)  # PENDING, STARTED, SUCCESS, FAILURE, etc.
print(result.result)  # Task result or error message
```

### View Celery logs:
```bash
# In worker terminal, watch for task execution logs
```

### Access Redis CLI (if using Redis):
```bash
redis-cli
> KEYS *
> GET celery-task-meta-xxxxx
```

## 11. Common Issues & Solutions

### Task not running:
- ✓ Redis/RabbitMQ is running
- ✓ Celery worker is running
- ✓ Celery beat is running
- ✓ Check logs for errors

### Email not sending:
- ✓ Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
- ✓ Gmail requires App Password (not regular password)
- ✓ Check email logs in Celery worker output

### OTP expired:
- OTP expires after 10 minutes
- Call `send_otp_email_task` again to generate new OTP

## 12. CSV Template Format

Download from Admin or create manually:

```csv
name,school_id,email,gender
John Doe,S12345,john@example.com,Male
Jane Smith,S12346,jane@example.com,Female
Bob Wilson,S12347,bob@example.com,Male
```

## 13. Production Deployment

For production, use:
- **Celery Worker:** systemd service or supervisor
- **Celery Beat:** systemd service or supervisor
- **Broker:** Redis or RabbitMQ (managed service like AWS ElastiCache)
- **Result Backend:** Redis or Database

See Celery documentation for detailed production setup.

---

**Questions?** Check Celery docs: https://docs.celeryproject.io/
