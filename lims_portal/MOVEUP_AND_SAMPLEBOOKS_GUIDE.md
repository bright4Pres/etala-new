# Student Move-Up & Sample Books Guide

## 🎓 Student Move-Up Feature

### Overview
The Student Move-Up feature allows administrators to automatically promote all students to the next grade level at the end of the school year. This eliminates the need to manually re-upload CSV files and re-activate student accounts.

### How It Works
- **Grade 7 → Grade 8**
- **Grade 8 → Grade 9**
- **Grade 9 → Grade 10**
- **Grade 10 → Grade 11**
- **Grade 11 → Grade 12**
- **Grade 12 → Deleted** (graduated students are removed)

### Usage Methods

#### Method 1: Admin Interface (Recommended for Librarians)
1. Log in to Django Admin
2. Go to any Grade section (Grade Seven, Grade Eight, etc.)
3. Select the **Action dropdown** at the top of the list
4. Choose **"🎓 Move All Students Up One Grade"**
5. Click **Go**
6. Review the confirmation page carefully
7. Click **"Confirm Move-Up"** to execute

⚠️ **Important**: The action affects ALL students across ALL grades, not just the selected items.

#### Method 2: Management Command (For Developers/Admins)
```bash
# Navigate to the project directory
cd lims_portal

# Preview the changes without executing (dry-run)
python manage.py moveup_students --dry-run

# Execute the actual move-up
python manage.py moveup_students
```

### Best Practices
1. **Before Move-Up:**
   - Remove students who dropped out or transferred
   - Verify Grade 12 students are ready to graduate
   - Consider backing up the database

2. **After Move-Up:**
   - Verify student counts in each grade
   - Check StudentActivation records
   - Notify students about their new grade status

### Safety Features
- **Transaction Safety**: All operations are wrapped in a database transaction
- **Dry-Run Mode**: Preview changes before committing (command-line only)
- **Confirmation Page**: Prevents accidental clicks in admin interface
- **Error Handling**: Detailed error messages if something goes wrong
- **Logging**: Complete summary of moved/deleted students

---

## 📚 Sample Books Feature

### Overview
The Sample Books feature generates realistic test data for the library system. Useful for development, testing, and training purposes.

### Usage

```bash
# Navigate to the project directory
cd lims_portal

# Create 100 sample books (default)
python manage.py init_sample_books

# Create custom number of books
python manage.py init_sample_books --count 50

# Clear existing books and create new samples
python manage.py init_sample_books --clear --count 200
```

### Options
- `--count N`: Generate N sample books (default: 100)
- `--clear`: Delete all existing books before creating samples

### Sample Data Includes
- **Realistic Titles**: Physics, Chemistry, Biology, Mathematics, Literature, etc.
- **Filipino Names**: Authors with common Filipino first and last names
- **Local Publishers**: Rex Bookstore, NBS, Anvil, UP Press, Ateneo Press, etc.
- **Multiple Types**: Books, Analytics, Articles, Thesis
- **Multiple Languages**: English, Filipino, Spanish, French
- **Organized Locations**: Science Section, Math Section, Literature Section, etc.
- **Unique Accession Numbers**: Format BK{YEAR}-{NUMBER}
- **All Available**: All books start with status='Available'

### Example Output
```
Creating 100 sample books...
  Created 10 books...
  Created 20 books...
  ...
==================================================
✅ Successfully created 100 sample books!
==================================================

Sample of created books:
  • BK2023-00100: Advanced Mathematics Vol. II (3rd Edition) by Sofia Reyes (Books)
  • BK2021-00099: Chemistry Fundamentals by Miguel Santos (Books)
  • BK2024-00098: Research Methods (Revised Edition) by Isabel Garcia (Article)
  • BK2022-00097: Filipino Panitikan Vol. I by Carlos Cruz (Books)
  • BK2019-00096: Data Analysis by Ana Flores (Analytics)
```

---

## 👥 Sample Students Feature

### Overview
The Sample Students feature generates realistic test data for all grade levels. Creates 30 students per grade (Grade 7-12) with Filipino names, unique school IDs, and email addresses.

### Usage

```bash
# Navigate to the project directory
cd lims_portal

# Create 30 sample students per grade level (default)
python manage.py init_sample_students

# Create custom number of students per grade
python manage.py init_sample_students --count 50

# Clear existing students and create new samples
python manage.py init_sample_students --clear --count 25
```

### Options
- `--count N`: Generate N sample students per grade level (default: 30)
- `--clear`: Delete all existing students before creating samples

### Sample Data Includes
- **Filipino Names**: Common Filipino first names, middle initials, and last names
- **Unique School IDs**: Format PSHS{YYYY}{Grade}{Number} (e.g., PSHS202607001)
- **Balanced Gender**: Random distribution of Male/Female
- **PSHS Email Addresses**: firstname.lastname@pshs.edu.ph format
- **Not Activated**: All students start with is_activated=False
- **All Grades**: Grade 7 through Grade 12 (30 students each = 180 total)

### Example Output
```
Creating 30 sample students for Grade 7...
  Created 10 students for Grade 7...
  Created 20 students for Grade 7...
  Created 30 students for Grade 7...
  ✅ Grade 7: 30 created, 0 skipped

Creating 30 sample students for Grade 8...
  ...
============================================================
🎓 Successfully created 180 sample students!
============================================================

Sample students created:

  Grade 7:
    • PSHS202607030: Juan A. Santos (Male) - juan.santos@pshs.edu.ph
    • PSHS202607029: Maria B. Garcia (Female) - maria.garcia@pshs.edu.ph

  Grade 8:
    • PSHS202608030: Pedro C. Rodriguez (Male) - pedro.rodriguez@pshs.edu.ph
    • PSHS202608029: Ana D. Martinez (Female) - ana.martinez@pshs.edu.ph
  ...
============================================================
💡 Tip: Students start as "not activated". Use the admin interface to activate them!
============================================================
```

---

## 🔧 Technical Details

### Student Move-Up Implementation
- **File**: `lims_portal/lims_app/management/commands/moveup_students.py`
- **Models Updated**: grade_Seven through grade_Twelve, StudentActivation
- **Processing Order**: Grade 11→12, 10→11, 9→10, 8→9, 7→8 (prevents conflicts)
- **Transaction Handling**: Atomic operations ensure data consistency

### Sample Books Implementation
- **File**: `lims_portal/lims_app/management/commands/init_sample_books.py`
- **Model**: Book
- **Fields Populated**: All fields including Title, authors, Publisher, dates, Location, etc.
- **Accession Numbers**: Automatically generated with uniqueness checks

### Sample Students Implementation
- **File**: `lims_portal/lims_app/management/commands/init_sample_students.py`
- **Models**: grade_Seven through grade_Twelve
- **Fields Populated**: name, school_id, gender, email, is_activated
- **School IDs**: Format PSHS{YYYY}{Grade}{Number} with uniqueness checks
- **Names**: Filipino first names, middle initials, and last names
- **Emails**: firstname.lastname@pshs.edu.ph format

---

## 📋 Workflow Example: End of School Year

### Week 1: Cleanup
1. Review all grade levels
2. Remove dropped students manually
3. Verify Grade 12 graduation list

### Week 2: Database Backup
```bash
# Backup database before major changes
python manage.py dumpdata > backup_$(date +%Y%m%d).json
```

### Week 3: Move-Up
1. Go to Admin → Grade Seven (or any grade page)
2. Actions → "🎓 Move All Students Up One Grade"
3. Review confirmation page
4. Click "Confirm Move-Up"
5. Verify success message with statistics

### Week 4: Verification
1. Check student counts in each grade
2. Verify no duplicate records
3. Test student login with new grade levels

---

## 🧪 Development Setup

### Quick Start with Sample Data
For development and testing, you can quickly populate your database with sample data:

```bash
# Create sample students (30 per grade = 180 total)
python manage.py init_sample_students

# Create sample books (100 books)
python manage.py init_sample_books

# Clear and recreate all sample data
python manage.py init_sample_students --clear --count 50
python manage.py init_sample_books --clear --count 200
```

### Sample Data Overview
- **Students**: 30 realistic Filipino students per grade level (Grades 7-12)
- **Books**: 100 diverse books with local publishers and PSHS-relevant subjects
- **Activation**: Students start unactivated (use admin to activate)
- **Status**: Books start as "Available" for borrowing

---

## ⚠️ Warnings

### Move-Up
- **IRREVERSIBLE**: Cannot undo after execution
- **DELETES Grade 12**: All graduating students are permanently removed
- **AFFECTS ALL STUDENTS**: Not just selected items in admin
- **BACKUP FIRST**: Always backup before running

### Sample Books
- **--clear DELETES ALL**: Be careful with the --clear flag in production
- **Development Only**: Intended for testing environments
- **Check Accession Numbers**: Ensure no conflicts with real books

### Sample Students
- **--clear DELETES ALL**: Removes all students from all grade levels
- **Unique Constraints**: Names and school_ids must be unique
- **Email Format**: Uses @pshs.edu.ph domain
- **Activation Required**: Students need admin activation before login

---

## 🆘 Troubleshooting

### Move-Up Fails
```python
# Check for errors in the admin messages
# Review the output for specific error messages
# Verify all grade models exist and are accessible
```

### Sample Books Duplicate Errors
```bash
# If you see "Skipped" messages, it's likely duplicate accession numbers
# Solution: Run with higher --count to generate unique numbers
python manage.py init_sample_books --count 150
```

### Sample Students Duplicate Errors
```bash
# If you see "Skipped" messages, it's likely duplicate names or school_ids
# Solution: Use --clear to start fresh, or run with different --count
python manage.py init_sample_students --clear --count 25
```

### Permission Errors
```bash
# Ensure you have superuser access
python manage.py createsuperuser
```

---

## 📞 Support

For issues or questions:
1. Check Django admin error messages
2. Review command output for detailed errors
3. Verify database integrity
4. Check logs for transaction failures

---

**Last Updated**: 2024
**Version**: 1.0
**Maintainer**: PSHS LIMS Development Team
