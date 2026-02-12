# ETALA Library Information Management System (LIMS)
## Comprehensive User Manual

**Version:** 2.0 (Offline Edition)  
**Last Updated:** February 12, 2026  
**System Type:** Standalone/Offline Library Management System

---

## Table of Contents

1. [System Overview](#system-overview)
2. [For Librarians - Daily Operations](#for-librarians---daily-operations)
3. [For IT Staff - System Administration](#for-it-staff---system-administration)
4. [Database Management](#database-management)
5. [Troubleshooting Guide](#troubleshooting-guide)
6. [Appendix](#appendix)

---

## System Overview

### What is ETALA LIMS?

ETALA LIMS is a **standalone library management system** designed to operate **without internet connectivity**. It manages:
- Book catalog and physical copies
- Student accounts (Grades 7-12)
- Borrowing and returns
- Overdue tracking
- Library analytics

### Key Features

✅ **Offline Operation** - No internet required  
✅ **Multi-copy Management** - Track individual book copies by accession number  
✅ **Barcode Support** - Quick checkout/return via barcode scanning  
✅ **Student Database** - Manage students across 6 grade levels  
✅ **Analytics Dashboard** - Borrowing trends, popular books, overdue tracking  
✅ **Backup System** - Built-in database backup functionality  

### System Requirements

- **Operating System:** Windows 10/11
- **Python:** 3.10 or higher
- **Database:** SQLite (included)
- **Browser:** Chrome, Firefox, or Edge
- **Network:** Offline/Local only

---

## For Librarians - Daily Operations

### 1. Getting Started

#### Logging In

1. Open your web browser
2. Navigate to: `http://127.0.0.1:8080/`
3. Click **"Library Admin"** in the sidebar
4. Enter your credentials:
   - **Username:** (Provided by IT)
   - **Password:** (Provided by IT)

#### Main Dashboard Overview

After logging in, you'll see:
- **Quick Stats**: Available books, borrowed books, overdue count
- **Recent Activity**: Latest checkouts and returns
- **Book Catalog**: Browse all books and copies
- **Student Accounts**: View all registered students

---

### 2. Book Management

#### Searching for Books

**From Records Page:**
1. Click **"Records"** in sidebar
2. Use search filters:
   - **Search bar**: Title, author, call number, accession number
   - **Book Type**: Analytics, Books, Thesis, Journal, etc.
   - **Language**: English, Filipino, etc.
   - **Location**: Shelving location
3. Results show all copies with availability status

**From Admin Dashboard:**
1. Use the **Books** tab
2. Search by title, author, or call number
3. View all physical copies and their status

#### Adding New Books

1. Go to **Admin Dashboard** → **Books** section
2. Click **"Add Book"** button
3. Fill in book details:
   - **Title** (required)
   - **Main Author** (required)
   - **Co-Author** (optional)
   - **Publisher** (optional)
   - **Edition** (optional)
   - **Call Number** (required, must be unique)
   - **Language** (default: English)
   - **Book Type** (default: Other)

4. Add physical copies in the **Copies List** field:
   ```
   Format: AccessionNumber, Location, Status
   
   Examples:
   ACC001, Main Library, Available
   ACC002, Reference Section, Available
   ACC003 | Science Wing | Available
   ```

5. Click **"Add Book"**

#### Managing Book Copies

**Viewing Copies:**
- Each book shows total copies and available count
- Click "Edit" to see all copies for a book

**Editing Copy Status:**
1. Find the book in the catalog
2. Click **"Edit"** button
3. Update copy information:
   - **Accession Number**: Unique identifier
   - **Location**: Physical location in library
   - **Status**: Available, Unavailable, Borrowed, Lost

4. Click **"Save Changes"**

**Deleting a Copy:**
1. Edit the book
2. Click **"Delete Copy"** next to the copy
3. Type "yes" to confirm
4. Copy is permanently removed

⚠️ **Warning:** Cannot delete copies that are currently borrowed!

---

### 3. Student Management

#### Viewing Students

1. Go to **Admin Dashboard** → **Users** tab
2. Students are organized by grade (7-12)
3. Search by:
   - Name
   - School ID
   - Grade level
   - Batch/cohort

#### Adding New Students

1. Click **"Add User"** button
2. Fill in required fields:
   - **Grade**: Select 7-12
   - **Full Name** (required)
   - **School ID** (required, must be unique)
   - **Email** (required)
   - **Batch/Cohort** (optional, e.g., "Antuilan")
   - **Gender**: Male/Female/Other

3. Click **"Add User"**

#### Editing Student Information

1. Find the student in the Users list
2. Click **"Edit"** button
3. Update any field:
   - Can change grade level (moves student between grades)
   - Can update school ID (must remain unique)
   - Can update name, email, batch

4. Click **"Save Changes"**

#### Deleting Students

1. Click **"Edit"** on the student
2. Click **"Delete User"** (red button)
3. Type "yes" to confirm
4. Student is permanently removed

⚠️ **Note:** Students with active borrowing records should not be deleted!

---

### 4. Checkout Process (Borrowing Books)

#### Method 1: Quick Checkout (Recommended)

1. In **Admin Dashboard**, find **Quick Checkout** section
2. Enter **Book Accession Number** (or scan barcode)
3. Enter **Student School ID**
4. Click **"Checkout"**

**System automatically:**
- Marks book as "Borrowed"
- Sets return date (1 day later, or Wednesday if borrowed Friday)
- Links book to student
- Creates borrow history record

#### Method 2: Manual Checkout

1. Go to **Checkout** page
2. Select book from dropdown (shows available copies only)
3. Enter student School ID
4. Click **"Checkout Book"**

#### Checkout Rules

📅 **Return Dates:**
- **Normal:** Next day return
- **Friday checkout:** Return on following Wednesday
- **Weekend adjustment:** Monday if calculated return falls on weekend

⚠️ **Pre-requisites:**
- Book copy must be "Available"
- Student must exist in database
- Book cannot already be borrowed

---

### 5. Return Process

#### Method 1: Barcode Scan Return (Fastest)

1. In **Admin Dashboard**, find **Quick Return** section
2. Scan book barcode or enter **Accession Number**
3. Click **"Return"**
4. System confirms return instantly

#### Method 2: Return from Borrowed Books List

1. View **Borrowed Books** section
2. Find the book in the list
3. Click **"Return"** button next to the entry
4. Book is marked as returned

**System automatically:**
- Marks book as "Available"
- Records return date and time
- Clears borrower information
- Updates borrow history

---

### 6. Overdue Book Management

#### Viewing Overdue Books

**Admin Dashboard:**
- Overdue books show in red in **Borrowed Books** section
- **Overdue Count** displayed in Quick Stats

**Analytics Page:**
- View full overdue list with:
  - Student name and ID
  - Book title
  - Days overdue
  - Expected return date

#### Handling Overdue Returns

1. Process return normally (same as on-time returns)
2. Note: System tracks that it was overdue in history
3. Manually communicate with student about late return policies

💡 **Tip:** Check overdue list daily to follow up with students

---

### 7. Reports and Analytics

#### Accessing Analytics

1. Click **"Analytics"** in sidebar
2. View comprehensive statistics:

**Core Metrics:**
- Total books in catalog
- Total registered students
- Currently borrowed books
- Overdue books count
- Book utilization rate

**Time-Based Statistics:**
- Filter by: Today, Week, Month, Quarter, Year
- New checkouts in period
- Returns in period
- New students registered

**Charts and Graphs:**
- **Monthly Borrowing Trends** (last 7 months)
- **Weekly Activity** (last 7 days)
- **Book Type Distribution** (pie chart)
- **Language Distribution** (top 5 languages)
- **Borrowing Heatmap** (calendar view)

**Top Lists:**
- Top 10 borrowers
- Most borrowed books
- Location statistics
- Batch/grade activity

#### Exporting Data

Currently manual export via Django admin:
1. Login to Django admin
2. Navigate to desired model
3. Use built-in export functionality

---

### 8. Daily Operations Checklist

#### Morning Routine
- [ ] Login to system
- [ ] Check overdue books list
- [ ] Process any pending returns
- [ ] Verify system is running properly

#### During Operation
- [ ] Process checkouts as students arrive
- [ ] Process returns as books come back
- [ ] Answer student inquiries using search
- [ ] Update book locations if needed

#### End of Day
- [ ] Review borrowed books list
- [ ] Note any missing/damaged books
- [ ] Backup database (weekly minimum)
- [ ] Log out of admin dashboard

---

## For IT Staff - System Administration

### 1. Initial Setup

#### Installing the System

**Prerequisites:**
```powershell
# 1. Install Python 3.10+
# Download from: https://www.python.org/downloads/

# 2. Verify installation
python --version  # Should show 3.10 or higher
```

**Installation Steps:**

```powershell
# 1. Navigate to project directory
cd C:\Users\[YourUser]\Downloads\Projects\etala-new\lims_portal

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
.\.venv\Scripts\Activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run migrations (first time only)
python manage.py migrate

# 6. Create superuser account
python manage.py createsuperuser
# Follow prompts to create admin account

# 7. Initialize sample data (optional)
python manage.py init_sample_students
python manage.py init_sample_books
```

#### Starting the Server

**Standard Startup:**
```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate

# 2. Start server
python manage.py runserver 8080

# Server runs at: http://127.0.0.1:8080/
```

**Auto-Start with Batch File:**

Double-click `CLICKMETOSTART.bat` in the lims_portal directory

The batch file contains:
```batch
@echo off
cd /d "%~dp0"
call .venv\Scripts\activate
python manage.py runserver 8080
pause
```

---

### 2. User Account Management

#### Creating Staff Accounts

**Via Django Admin:**
```powershell
python manage.py createsuperuser
```

**Via Django Shell:**
```python
python manage.py shell

from django.contrib.auth.models import User

# Create librarian account
user = User.objects.create_user(
    username='librarian1',
    password='SecurePassword123!',
    email='librarian@school.edu',
    is_staff=True  # Grants admin access
)
```

#### Resetting Passwords

**Command Line:**
```powershell
python manage.py changepassword username
```

**Via Django Admin:**
1. Login to admin: `http://127.0.0.1:8080/admin/`
2. Go to **Users**
3. Select user
4. Click **"Change password"**
5. Enter new password twice

---

### 3. Database Management

#### Understanding the Database

**Location:** `lims_portal/db.sqlite3`

**Main Tables:**
- `lims_app_book` - Book titles and metadata
- `lims_app_bookcopy` - Physical book copies
- `lims_app_borrowhistory` - Checkout/return records
- `lims_app_grade_seven` through `lims_app_grade_twelve` - Student records

#### Creating Backups

**Manual Backup:**
```powershell
# Copy database file
Copy-Item db.sqlite3 -Destination "backups/db_$(Get-Date -Format 'yyyyMMdd_HHmmss').sqlite3"
```

**Using Django Admin:**
1. Login to admin dashboard
2. Scroll to **"System Maintenance"** section
3. Click **"Create Backup"**
4. Backup saved to: `backups/[timestamp]/`

**Backup Contents:**
- `db.sqlite3` - Full database
- `books.json` - Book catalog
- `book_copies.json` - Copy inventory
- `users.json` - All student records
- `grade12_graduating.json` - Grade 12 only (for archiving)

#### Restoring from Backup

```powershell
# 1. Stop the server (Ctrl+C)

# 2. Backup current database
Copy-Item db.sqlite3 -Destination db_before_restore.sqlite3

# 3. Restore from backup
Copy-Item backups/[timestamp]/db.sqlite3 -Destination db.sqlite3

# 4. Restart server
python manage.py runserver 8080
```

#### Database Maintenance

**Check for issues:**
```powershell
python manage.py check
```

**Optimize database:**
```powershell
# SQLite auto-vacuums, but you can manually optimize:
sqlite3 db.sqlite3 "VACUUM;"
```

---

### 4. Student Management Commands

#### Bulk Import Students from CSV

**CSV Format:**
```csv
name,school_id,gender,email
Juan dela Cruz,2024-001,Male,juan.delacruz@pshs.edu.ph
Maria Santos,2024-002,Female,maria.santos@pshs.edu.ph
```

**Import Process:**
1. Login to Django admin: `http://127.0.0.1:8080/admin/`
2. Click on a grade level (e.g., "Grade Sevens")
3. Click **"Import CSV"** button
4. Upload your CSV file
5. Review and confirm import

**Command Line Alternative:**
```python
python manage.py shell

from lims_app.models import grade_Seven
import csv

with open('students.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        grade_Seven.objects.create(
            name=row['name'],
            school_id=row['school_id'],
            gender=row['gender'],
            email=row['email'],
            batch=row.get('batch', '')
        )
```

#### Year-End Student Move-Up

**Moving students up one grade level:**

```powershell
# Preview changes (dry run)
python manage.py moveup_students --dry-run

# Execute move-up
python manage.py moveup_students
```

**What happens:**
- Grade 7 → Grade 8
- Grade 8 → Grade 9
- Grade 9 → Grade 10
- Grade 10 → Grade 11
- Grade 11 → Grade 12
- Grade 12 → Archived (deleted from system)

**Backup is created automatically before executing!**

⚠️ **Critical:** Always backup database before moving students up!

---

### 5. Book Management

#### Bulk Import Books

**CSV Format:**
```csv
Title,mainAuthor,Publisher,callNumber,Language,Type,AccessionNumber,Location,Status
Chemistry 101,Dr. Smith,Publisher Inc,QD001,English,Books,ACC001,Main Library,Available
Chemistry 101,Dr. Smith,Publisher Inc,QD001,English,Books,ACC002,Main Library,Available
```

**Features:**
- Multiple copies with same call number = same book
- Accession numbers must be unique
- Status: Available, Unavailable, Borrowed, Lost

#### Generating Barcodes

System includes barcode generation for accession numbers:

**Via Django Admin:**
1. Go to **Book Copies** in admin
2. Select copies
3. Actions → **"Export barcodes"**
4. Print barcode sheet

**Barcode Format:** Code 128 (standard library format)

---

### 6. System Configuration

#### Settings File: `lims_portal/settings.py`

**Key Settings:**

```python
# Debug Mode (turn OFF for production)
DEBUG = False  # Should be False in production

# Allowed Hosts
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Time Zone
TIME_ZONE = 'Asia/Manila'  # Adjust for your location

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### File Structure

```
lims_portal/
├── db.sqlite3                  # Main database
├── manage.py                   # Django management script
├── CLICKMETOSTART.bat         # Quick start script
├── requirements.txt           # Python dependencies
├── SYSTEM_MANUAL.md          # This file
├── backups/                   # Backup directory
├── lims_app/                  # Main application
│   ├── models.py             # Database models
│   ├── views.py              # Application logic
│   ├── urls.py               # URL routing
│   ├── admin.py              # Admin configuration
│   ├── templates/            # HTML templates
│   ├── static/               # CSS, JS, images
│   └── management/           # Custom commands
└── lims_portal/              # Project settings
    ├── settings.py           # Configuration
    ├── urls.py               # Main URL config
    └── wsgi.py               # WSGI config
```

---

### 7. Monitoring and Logs

#### Checking System Status

```powershell
# View all processes
python manage.py check --deploy

# Check for migrations
python manage.py showmigrations

# View database statistics
python manage.py dbshell
.tables
.schema lims_app_book
.exit
```

#### Viewing Logs

**Terminal Output:**
- Server logs appear in terminal where `runserver` is running
- Shows all HTTP requests and errors

**Django Debug Info:**
- When DEBUG=True, detailed error pages show
- Includes stack traces and variable values

---

### 8. Security Best Practices

#### Access Control

✅ **Do:**
- Use strong passwords (12+ characters)
- Change default passwords immediately
- Limit staff accounts to necessary personnel
- Lock workstation when leaving

❌ **Don't:**
- Share admin credentials
- Use "admin/admin" or simple passwords
- Leave DEBUG=True in production
- Expose system to internet

#### Data Protection

- **Daily:** Keep system running, monitor for errors
- **Weekly:** Create backup via admin dashboard
- **Monthly:** Verify backup integrity
- **Yearly:** Archive graduated students before move-up

#### Network Security

Since system is offline:
- ✅ No risk of external attacks
- ✅ No need for firewall configuration
- ⚠️ Protect physical access to server machine
- ⚠️ Encrypt backups if stored on USB drives

---

## Database Management

### Schema Overview

#### Books System

**Book Model** (Book titles/metadata)
- Title, Authors, Publisher, Edition
- Call Number (unique identifier)
- Language, Type
- Has many BookCopies

**BookCopy Model** (Physical copies)
- Accession Number (unique, barcode ID)
- Location (shelf/section)
- Status (Available, Borrowed, Lost, Unavailable)
- Belongs to one Book

**BorrowHistory Model** (Checkout records)
- Links BookCopy to Student (by school_id)
- Borrow date, Return date
- Returned status
- Overdue tracking

#### Student System

**Grade Models** (Six separate tables)
- grade_Seven, grade_Eight, ... grade_Twelve
- Student name, school_id (unique)
- Gender, batch/cohort
- Created timestamp

**Why separate tables?**
- Easy year-end move-up
- Better performance for grade-specific queries
- Simple archiving of graduates

---

### Data Relationships

```
Book (1) ─────→ (Many) BookCopy
                          │
                          │ borrowed by
                          ↓
                    BorrowHistory ←─── Student (grade_model)
```

---

### Common Queries

#### Find overdue books:
```sql
SELECT * FROM lims_app_borrowhistory 
WHERE returned = 0 
AND return_date < datetime('now');
```

#### Count books by status:
```sql
SELECT status, COUNT(*) 
FROM lims_app_bookcopy 
GROUP BY status;
```

#### Most active borrowers:
```sql
SELECT accountName, COUNT(*) as borrows 
FROM lims_app_borrowhistory 
GROUP BY accountID 
ORDER BY borrows DESC 
LIMIT 10;
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: Server Won't Start

**Error:** `Port 8080 is already in use`

**Solution:**
```powershell
# Find process using port 8080
netstat -ano | findstr :8080

# Kill the process (use PID from above)
taskkill /PID [ProcessID] /F

# Restart server
python manage.py runserver 8080
```

---

#### Issue 2: "No module named django"

**Error:** `ModuleNotFoundError: No module named 'django'`

**Solution:**
```powershell
# Ensure virtual environment is activated
.\.venv\Scripts\Activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

#### Issue 3: Database Locked

**Error:** `database is locked`

**Solution:**
```powershell
# 1. Close all database connections
# 2. Restart server
# 3. If persists, check for orphaned processes:

Get-Process python | Stop-Process -Force
```

---

#### Issue 4: Migration Errors

**Error:** `No migrations to apply` but tables missing

**Solution:**
```powershell
# Reset migrations (CAREFUL - only if development)
python manage.py migrate --fake lims_app zero
python manage.py migrate lims_app
```

---

#### Issue 5: Static Files Not Loading

**Error:** CSS/JS not loading, page looks broken

**Solution:**
```powershell
# Collect static files
python manage.py collectstatic --no-input

# Ensure DEBUG=True in settings.py for development
```

---

#### Issue 6: Cannot Delete Book Copy

**Error:** "Cannot delete copy - currently borrowed"

**Solution:**
1. Check **Borrowed Books** list
2. Find the borrow record
3. Return the book first
4. Then delete the copy

---

#### Issue 7: HTTPS Warnings in Terminal

**Warning:** `You're accessing the development server over HTTPS`

**Solution:**
- **Ignore** - These are harmless
- Ensure you access via `http://` not `https://`
- Clear browser HSTS cache if Chrome auto-redirects

---

#### Issue 8: Barcode Scanner Not Working

**Symptoms:** Scanner types garbage or doesn't input

**Solution:**
1. Ensure scanner is in **keyboard emulation mode**
2. Check scanner suffix (should send "Enter" after scan)
3. Test in Notepad to verify scanner output
4. Click into input field before scanning

---

### Emergency Procedures

#### System Crash Recovery

1. **Stop server** (Ctrl+C)
2. **Check database integrity:**
   ```powershell
   sqlite3 db.sqlite3 "PRAGMA integrity_check;"
   ```
3. **If corrupted, restore from backup:**
   ```powershell
   Copy-Item backups/[latest]/db.sqlite3 -Destination db.sqlite3
   ```
4. **Restart server**

#### Data Loss Prevention

- Keep backups in **multiple locations**:
  - Local: `backups/` folder
  - USB drive (weekly)
  - Network drive (if available offline)
  
- Test backup restoration **quarterly**

---

### Getting Help

#### Error Reporting

When reporting issues, include:

1. **Error message** (full text)
2. **What you were doing** (steps to reproduce)
3. **When it started** (after what change?)
4. **System info:**
   ```powershell
   python --version
   python manage.py --version
   ```

#### Support Contacts

- **IT Department:** [Your IT Contact]
- **System Developer:** [Developer Contact]
- **Django Documentation:** https://docs.djangoproject.com/

---

## Appendix

### A. Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Search books | Ctrl+F (on records page) |
| Quick logout | ALT+L (admin dashboard) |
| Refresh page | F5 |
| Stop server | Ctrl+C (in terminal) |

---

### B. Django Management Commands Reference

```powershell
# Database
python manage.py migrate              # Apply database migrations
python manage.py makemigrations      # Create new migrations
python manage.py dbshell             # Open database shell

# Users
python manage.py createsuperuser     # Create admin account
python manage.py changepassword      # Change user password

# Students
python manage.py moveup_students     # Year-end grade promotion
python manage.py init_sample_students # Create sample data

# Books
python manage.py init_sample_books   # Create sample catalog

# Maintenance
python manage.py check               # Check for issues
python manage.py check --deploy      # Production checks
python manage.py collectstatic       # Gather static files

# shell
python manage.py shell               # Python shell with Django
```

---

### C. File Permissions

Ensure these files are writable:
- `db.sqlite3` - Database file
- `backups/` - Backup directory
- `static/` - Static files (if using collectstatic)

**Windows permissions:**
```powershell
# Check permissions
icacls db.sqlite3 backups/

# Grant permissions if needed
icacls db.sqlite3 /grant Everyone:F
icacls backups/ /grant Everyone:F
```

---

### D. System Capacity

**Current Limits:**
- Books: Unlimited (SQLite supports billions)
- Students: Unlimited per grade
- Borrow History: Unlimited
- Concurrent Users: 1-5 (development server)

**For larger scale:**
- Consider PostgreSQL instead of SQLite
- Use production WSGI server (gunicorn, waitress)
- Add caching (Redis, Memcached)

---

### E. Barcode Standards

**Supported formats:**
- Code 128 (recommended)
- Code 39
- EAN-13

**Accession Number Format:**
```
Recommended: ABC0001, ABC0002, ...
- 3 letter prefix (constant)
- 4+ digit number (sequential)
- Total length: 7-10 characters
```

**Why this format?**
- Easy to scan
- Human-readable
- Sortable
- Unique

---

### F. CSV Import Templates

**Students Template:**
```csv
name,school_id,gender,email,batch
Juan dela Cruz,2024-7001,Male,juan.delacruz@school.edu,Antuilan
Maria Santos,2024-7002,Female,maria.santos@school.edu,Bakunawa
Pedro Reyes,2024-7003,Male,pedro.reyes@school.edu,Antuilan
```

**Books Template:**
```csv
Title,mainAuthor,coAuthor,Publisher,Edition,callNumber,Language,Type
Chemistry Basics,Dr. Smith,Dr. Jones,Science Press,3rd,QD001,English,Books
Physics 101,Prof. Brown,,Academic Pub,1st,QC001,English,Books
```

**Book Copies Template:**
```csv
AccessionNumber,BookCallNumber,Location,Status
SCI001,QD001,Main Library,Available
SCI002,QD001,Reference Section,Available
SCI003,QC001,Science Wing,Available
```

---

### G. Glossary

**Accession Number** - Unique identifier for a physical book copy (e.g., "ABC001")

**Call Number** - Library classification number for a book title (e.g., "QD001")

**Book Copy** - Physical instance of a book (one book title can have multiple copies)

**Borrow History** - Record of checkout and return for a book copy

**Django** - Web framework used to build this system

**SQLite** - Database engine storing all data

**Virtual Environment** - Isolated Python environment for the project

**WSGI** - Web Server Gateway Interface (how Python serves web pages)

**Overdue** - Book not returned by expected return date

**Dry Run** - Test mode that previews changes without saving them

---

### H. Quick Reference Card

**🚀 Starting the System**
```powershell
cd C:\...\lims_portal
.\.venv\Scripts\Activate
python manage.py runserver 8080
```
Access: `http://127.0.0.1:8080/`

**📚 Quick Checkout**
1. Scan/enter book accession number
2. Enter student school ID
3. Click "Checkout"

**↩️ Quick Return**
1. Scan/enter book accession number
2. Click "Return"

**💾 Create Backup**
1. Login to admin dashboard
2. Click "Create Backup"
3. Wait for confirmation

**🔍 Search Books**
- Records page → Search bar
- Filter by type, language, location

**📊 View Analytics**
- Analytics page → Select time period
- View borrowing trends and statistics

---

## Support and Updates

### System Maintenance Schedule

- **Daily:** Monitor system operation
- **Weekly:** Database backup
- **Monthly:** Review analytics, check for issues
- **Quarterly:** Test backup restoration
- **Yearly:** Student move-up, archive graduates

### Version History

- **v2.0** (Feb 2026) - Offline edition, removed email/OTP features
- **v1.5** (Dec 2025) - Added multi-copy support
- **v1.0** (Sep 2025) - Initial release

---

## Conclusion

This manual covers all aspects of the ETALA LIMS for both librarians and IT staff. For questions or additional training, contact your IT department.

**Remember:**
- ✅ Always backup before major changes
- ✅ Test in dry-run mode when available
- ✅ Document any customizations
- ✅ Keep system secure with strong passwords

**Happy Library Managing! 📚**

---

**Document Information**
- Manual Version: 2.0
- Last Updated: February 12, 2026
- Maintained by: IT Department
- System Version: ETALA LIMS v2.0 (Offline Edition)
