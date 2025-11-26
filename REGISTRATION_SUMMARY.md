# Registration Flow Summary

## Answer to Your Questions

### "When does it know to send the email OTP?"

**Answer**: When the user clicks "Send OTP" in Step 3 (Email Verification step).

The flow is:
1. User selects grade → picks student name → enters email
2. Clicks "Send OTP"
3. Backend verifies email matches the one in database
4. **If it matches → generates OTP → sends email via Celery**
5. User gets notification "OTP sent to email@address"
6. User then enters the OTP in Step 4

---

## Your Registration Modal - Step by Step

### Step 1: Select Grade
```
[Dropdown: Grade 7, 8, 9, 10, 11, 12]
[Next Button]
```
- User picks their grade

### Step 2: Select Student Name
```
[Dropdown: Populated with all students from that grade]
  - Shows: "Student Name (School ID)"
[Back] [Next Button]
```
- Backend fetches all students from database for that grade
- User selects their name

### Step 3: Verify Email
```
[Text: "Confirm this email matches your school record: student@email.com"]
[Input: Email field]
[Back] [Send OTP Button]
```
- Shows the email from database
- User enters their email
- User clicks "Send OTP"
- **CROSS-REFERENCE**: Compares entered email with database email
- **IF MATCH**: Generates & sends OTP

### Step 4: Enter OTP
```
[Text: "We've sent a 6-digit OTP to your email"]
[Input: 6-digit OTP]
[Text: "OTP expires in 10 minutes"]
[Back] [Activate Account Button] [Resend OTP link]
```
- User enters OTP received in email
- Clicks "Activate Account"
- Verify OTP matches & hasn't expired
- Account activated ✓

---

## OTP Generation & Verification

### Generation (Step 3 - when "Send OTP" clicked)
```python
# Happens in views_otp.py: verify_student_email()

activation = StudentActivation.objects.get_or_create(
    school_id=student.school_id,
    # ... other fields
)

otp = activation.generate_otp()  # Returns: "423891"
send_otp_email_task.delay(activation.email, otp, activation.name)  # Sends async
```

**What it does:**
- Generates random 6-digit code (0-9)
- Stores in database
- Stores timestamp for 10-minute expiry
- Sends via Celery email task

### Verification (Step 4 - when OTP entered)
```python
# Happens in views_otp.py: verify_otp()

activation = StudentActivation.objects.get(id=activation_id)

# Check 1: Is OTP expired?
if activation.is_otp_expired():  # Checks if > 10 minutes
    return "OTP has expired"

# Check 2: Does entered OTP match?
if activation.verify_otp(entered_otp):  # Compares "123456" vs stored
    return "Account activated!"
else:
    return "Invalid OTP"
```

**What it checks:**
1. Timestamp: Was OTP generated < 10 minutes ago?
2. Code: Does entered code match stored code exactly?
3. If both pass: Mark account as activated ✓

---

## New Files Created

1. **`views_otp.py`** - 4 new API endpoints:
   - `get_students_by_grade()` - Fetch students for a grade
   - `verify_student_email()` - **SENDS OTP HERE** ✓
   - `verify_otp()` - Validate OTP & activate
   - `resend_otp()` - Generate & send new OTP

2. **Updated `urls.py`** - Added 4 API routes

3. **Updated `home.html`** - New registration modal with 4 steps

4. **OTP_FLOW_GUIDE.md** - Complete documentation

---

## Key Points

✅ **Email sent on "Send OTP" button click** (Step 3)  
✅ **User email cross-referenced** with database record  
✅ **OTP valid for 10 minutes** only  
✅ **Can resend OTP** if not received  
✅ **Sent asynchronously** via Celery (non-blocking)  
✅ **Auto-expires after verification** or timeout  

---

## Next Steps

1. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. Start services:
   ```bash
   # Terminal 1
   redis-server
   
   # Terminal 2
   celery -A lims_portal worker -l info
   
   # Terminal 3
   python manage.py runserver
   ```

3. Test:
   - Go to home page
   - Click Register button
   - Follow 4-step flow
   - Check Celery logs for email sending
