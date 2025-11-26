# OTP Registration & Activation Flow Guide

## Overview

The new registration system uses a **4-step verification process** with OTP (One-Time Password) to securely activate student accounts.

---

## Step-by-Step Flow

### **Step 1: Grade Selection**
- User opens registration modal
- Selects their grade (7-12)
- Clicks "Next"
- **Backend**: `/api/get-students/` endpoint fetches all students for that grade

### **Step 2: Student Selection**
- Dropdown populates with students from selected grade
- User selects their name (displays as "Name (School ID)")
- Clicks "Next"
- **Backend**: Stores grade and student ID in session state

### **Step 3: Email Verification**
- User enters their email address
- System displays the email from database for confirmation
- User verifies it matches
- Clicks "Send OTP"
- **Backend Flow**:
  1. `/api/verify-email/` receives the request
  2. Compares entered email with database email
  3. If match: Creates/updates `StudentActivation` record
  4. Generates 6-digit OTP via `StudentActivation.generate_otp()`
  5. **SENDS EMAIL** via Celery task: `send_otp_email_task.delay(...)`
  6. Returns activation ID to frontend

### **Step 4: OTP Verification**
- User enters 6-digit OTP received in email
- Clicks "Activate Account"
- **Backend Flow**:
  1. `/api/verify-otp/` receives the request
  2. Calls `StudentActivation.verify_otp(entered_otp)`
  3. Method checks:
     - If OTP hasn't expired (10-minute window)
     - If OTP matches the generated one
  4. If valid: Sets `is_activated = True` and saves
  5. Returns success and student info to frontend

---

## When is OTP Sent?

**OTP IS SENT in Step 3 (Email Verification Step)**

Flow:
```
User clicks "Send OTP" 
    ↓
verify_email endpoint cross-references email
    ↓
Email matches? YES
    ↓
Generate 6-digit OTP → StudentActivation.generate_otp()
    ↓
Celery task queues → send_otp_email_task.delay(email, otp, name)
    ↓
Email sent asynchronously ✓
    ↓
User receives OTP → Enters in Step 4
```

---

## OTP Generation Details

### Generation
```python
# In StudentActivation.generate_otp():
otp = ''.join(random.choices(string.digits, k=6))
otp_created_at = timezone.now()
```

**Result**: 6-digit code like `423891`

### Storage
- Stored in `StudentActivation.otp` field
- Timestamp stored in `otp_created_at`
- Can be regenerated (resent)

### Expiry
```python
# In StudentActivation.is_otp_expired():
expiry_time = otp_created_at + timedelta(minutes=10)
return timezone.now() > expiry_time
```

**Result**: OTP valid for exactly 10 minutes

### Verification
```python
# In StudentActivation.verify_otp(entered_otp):
1. Check if expired → return False
2. Compare entered_otp == stored otp → return True/False
3. If match: Set is_activated = True, save
```

---

## Resend OTP Feature

If user doesn't receive OTP or it expires:

1. User clicks "Didn't receive OTP? Resend"
2. `/api/resend-otp/` generates NEW 6-digit OTP
3. Updates `otp` and `otp_created_at` fields
4. Sends via Celery task again
5. User gets new code in email

**Important**: Old OTP becomes invalid when new one is generated

---

## API Endpoints

### 1. Get Students by Grade
```
POST /api/get-students/
Content-Type: application/json

{
  "grade": 7
}

Response:
{
  "success": true,
  "students": [
    {"id": 1, "name": "John Doe", "school_id": "13-2020-001", "email": "john@school.com"},
    {"id": 2, "name": "Jane Smith", "school_id": "13-2020-002", "email": "jane@school.com"}
  ]
}
```

### 2. Verify Email & Send OTP
```
POST /api/verify-email/
Content-Type: application/json

{
  "grade": 7,
  "student_id": 1,
  "email": "john@school.com"
}

Response (Success):
{
  "success": true,
  "message": "OTP sent to john@school.com",
  "activation_id": 42
}

Response (Error):
{
  "success": false,
  "error": "Email does not match the student record"
}
```

### 3. Verify OTP
```
POST /api/verify-otp/
Content-Type: application/json

{
  "activation_id": 42,
  "otp": "423891"
}

Response (Success):
{
  "success": true,
  "message": "Account activated successfully!",
  "student_name": "John Doe",
  "school_id": "13-2020-001"
}

Response (Error - Expired):
{
  "success": false,
  "error": "OTP has expired. Please request a new one."
}

Response (Error - Invalid):
{
  "success": false,
  "error": "Invalid OTP. Please try again."
}
```

### 4. Resend OTP
```
POST /api/resend-otp/
Content-Type: application/json

{
  "activation_id": 42
}

Response:
{
  "success": true,
  "message": "OTP resent to john@school.com"
}
```

---

## Database Models

### StudentActivation
```python
school_id          # Unique identifier (e.g., "13-2020-001")
name               # Student's full name
email              # Student's email
grade              # Grade level (7-12)
otp                # 6-digit code (nullable until generated)
otp_created_at     # When OTP was generated (for expiry check)
is_activated       # Boolean: Account activated status
activated_at       # When account was activated
created_at         # Record creation timestamp
```

---

## Email Sending via Celery

### Task: `send_otp_email_task`

Located in `lims_app/tasks.py`:

```python
@shared_task
def send_otp_email_task(email, otp, student_name):
    """Send OTP via email asynchronously."""
    subject = "Your eTala Library Account Activation"
    message = f"""
    Hello {student_name},
    
    Your OTP code is: {otp}
    
    This code expires in 10 minutes.
    
    Do not share this code with anyone.
    
    Best regards,
    eTala Library Team
    """
    
    try:
        send_mail(subject, message, settings.EMAIL_USER, [email])
        # Logs success
    except Exception as e:
        # Logs error, retries automatically
```

### Prerequisites
1. **Celery Worker Running**: `celery -A lims_portal worker -l info`
2. **Redis Broker Running**: `redis-server`
3. **Email Configuration** in `.env`:
   - `EMAIL_USER=your-email@gmail.com`
   - `EMAIL_PASS=your-app-password`

### How It Works
1. View calls `send_otp_email_task.delay(email, otp, name)`
2. Task queued to Redis
3. Celery worker picks it up
4. Sends email asynchronously (non-blocking)
5. User immediately gets response "OTP sent..."
6. Email arrives in 1-5 seconds

---

## Security Features

✅ **Email Validation**: Entered email must match database  
✅ **Time-based Expiry**: OTP valid for only 10 minutes  
✅ **One-time Use**: OTP consumed after verification  
✅ **Resend Capability**: Can request new OTP if needed  
✅ **Rate Limiting**: (Optional - can be added)  
✅ **CSRF Protection**: All POST requests require CSRF token  

---

## Testing the Flow

### 1. Start Services
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
celery -A lims_portal worker -l info

# Terminal 3: Django
python manage.py runserver
```

### 2. Test Steps
1. Navigate to home page
2. Click "Register" button
3. Select Grade 7
4. Select any student
5. Enter their email (must match database)
6. Click "Send OTP"
7. Check console/Redis logs for email task
8. Manually check email or look in test email backend
9. Enter OTP
10. Verify success message

### 3. Debug
- Check Celery worker logs for email sending
- Verify Redis connection: `redis-cli ping`
- Check Django console for errors
- Verify `.env` has correct email credentials

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "OTP sent..." but no email | Check Celery worker is running |
| OTP expired error | OTP valid only 10 min, click Resend |
| Email doesn't match | Verify exact email in database |
| "Invalid OTP" | Check entered code matches exactly |
| Celery connection error | Start Redis: `redis-server` |
| Task not executing | Check `celery -A lims_portal worker -l info` |

---

## Next Steps (Optional Enhancements)

- [ ] Add rate limiting to prevent brute force OTP attempts
- [ ] Implement CAPTCHA for additional security
- [ ] Add SMS OTP as fallback
- [ ] Create admin dashboard to monitor activations
- [ ] Add email verification for typos
- [ ] Implement login with activated account
