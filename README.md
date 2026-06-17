# eTala OPAC

eTala (Enhanced Technology-Assisted Library Access) is a web-based library management system and OPAC (Online Public Access Catalogue) built for PSHS-ZRC in Dipolog City. It was originally a student project under the SCALE Program by six scholars from batch Antuilan, and it replaced the old paper-based cataloging the library was using.

The system has two main sides: a public-facing OPAC portal where students can browse and search the library catalog, and an admin dashboard where the librarian manages everything -- books, students, checkouts, returns, analytics, and more.

---

## What it does

**Public side (OPAC)**

- Homepage with a brief intro to the project and the library
- Book records page with a searchable, filterable DataTable showing all books and their availability
- Expanding rows show full book details and copy-level info (accession number, location, status)
- Search works with URL sync so you can share a search link

**Admin side**

- Login page with rate limiting (5 failed attempts = 15 minute lockout)
- Dashboard with borrowed books displayed as cards, color-coded by overdue status
- Sidebar panels for Books and Students that slide in without navigating away
- Checkout view for scanning or typing an accession number + student ID to borrow a book
- Return view for returning via barcode/accession number or clicking a card
- Recent activity feed on the right panel
- Analytics page with charts (monthly borrows, weekly activity, book types, language distribution, gender breakdown by grade, borrow heatmap, top borrowers, most borrowed books, location stats, and more)
- Export analytics as CSV or JSON
- Book management: add books with multiple physical copies per record, edit book info and copy status/location, delete individual copies
- Student management: add students, edit/delete, import via CSV, and a Move-Up feature that promotes all students one grade level and graduates Grade 12
- Manual backup to a timestamped folder (saves db.sqlite3 + JSON exports of all data)

---

## Tech stack

- **Backend:** Django (Python)
- **Database:** SQLite (via Django ORM)
- **Frontend:** Vanilla HTML/CSS/JS, some Bootstrap for the records table
- **DataTables:** jQuery DataTables with Bootstrap 5 integration for the records page
- **Charts:** Presumably Chart.js (referenced in analytics context, not shown here but it's in the template)
- **Auth:** Django's built-in auth system, staff_member_required decorator for admin routes

No React, no Vue, nothing fancy. Just Django templates and some JavaScript sprinkled where needed.

---

## Project structure (rough overview)

```
etala/
  library/               # main Django app
    models.py            # Book, BookCopy, BorrowHistory, students models
    views.py             # all views (home, records, admin dashboard, analytics, etc.)
    urls.py              # URL routing
    management/
      commands/
        moveup_students.py  # custom management command for grade move-up
  templates/
    home.html            # landing page
    records.html         # public OPAC records page
    cadmin.html          # admin dashboard (the big one)
    analytics.html       # analytics page
    admin_login.html     # login page
    base_portal.html     # base template for public pages
    ...
  static/
    Scripts/
      css/
        cadmin.css       # admin styles
        normalize.css
        ...
      js/
        cadmin.js        # admin JS (sidebar toggle, search, view switching)
        jquery-3.6.0.min.js
        jquery.dataTables.min.js
        ...
    img/
      etalalogo.svg
      pisaylogo.svg
  db.sqlite3             # the database (not committed to git, hopefully)
  backups/               # auto-generated backup folder
  manage.py
```

---

## Data models

**Book** -- one record per unique call number. Stores bibliographic info: title, authors, publisher, edition, call number, language, type, place of publication, dates, editors, acquisition status.

**BookCopy** -- each physical copy of a book. Has its own accession number, location, and status (Available / Borrowed / Unavailable / Lost). Foreign key to Book. This is what actually gets borrowed.

**BorrowHistory** -- a log of every checkout. Stores book title, accession number, student ID, student name, borrow date, due date, and whether it's been returned. Has a FK to BookCopy for modern records; older records use the raw accession number field for compatibility.

**students** -- yes, lowercase model name, it is what it is. Stores student name, school_id, email, grade level (7-12), batch, section, gender, and created_at.

---

## How the admin dashboard works

The dashboard (`cadmin.html` + `admin_dashboard` view) is a single-page-ish experience. There are three main views on the content area -- borrowed, checkout, and return -- toggled by the sidebar icons. The sidebar also has sliding panels for Books and Students management.

All forms POST back to the same `admin_dashboard` URL with an `action` field that tells the view what to do. After processing, it renders the page again with Django messages instead of redirecting, so you stay on the same view. The `active_view` field in the POST body tells the template which panel to show after reload.

The book sidebar shows every book with its copy count and availability, and has an inline search. The student sidebar groups students by grade in collapsible `<details>` elements. Both have search that filters in real time without a page reload.

---

## Setup

Assuming you have Python 3.10+ and pip:

```bash
git clone https://github.com/yourusername/etala.git
cd etala

python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

pip install django

python manage.py migrate
python manage.py createsuperuser

python manage.py runserver
```

Then go to `http://127.0.0.1:8000/` for the public portal and `http://127.0.0.1:8000/admin-login/` for the library admin dashboard (use the superuser you just created).

Note: the superuser needs `is_staff = True` to access the admin dashboard, which it will have by default when you use `createsuperuser`.

---

## CSV import format for students

The import feature accepts a CSV file with these columns:

```
name, grade level, section, email, school_id
```

`section`, `email`, and `school_id` are all optional. If `school_id` is missing, one gets auto-generated based on the current year and grade. Column headers are normalized so "Grade Level", "grade-level", and "gradelevel" all work.

---

## The Move-Up feature

Move-Up is a one-click operation (with password confirmation) that:

1. Takes a backup snapshot of Grade 12 students to a JSON file
2. Runs the `moveup_students` management command which increments every student's grade level by 1
3. Deletes (or graduates out) Grade 12 students

This is a destructive operation. It auto-saves a backup to `backups/moveup_<timestamp>/` before running. You should also run a full backup first just to be safe.

---

## Backup system

Hitting the Backup button in the dashboard creates a timestamped folder under `backups/` with:

- `db.sqlite3` -- a copy of the database
- `books.json` -- all book records
- `book_copies.json` -- all copy records
- `users.json` -- all students grouped by grade
- `grade12_graduating.json` -- Grade 12 students specifically
- `totals.json` -- summary counts

These are just flat file dumps. There's no automated restore UI, you'd have to manually copy the db back if you need to roll back.

---

## Known limitations / things to be aware of

- SQLite is fine for a school library but if this ever needed to scale up or handle concurrent writes under heavy load, you'd want to switch to Postgres.
- The `students` model has lowercase naming which is inconsistent with Django conventions but it works.
- `borrowed_by` on BookCopy stores the student ID as a string, not a FK. This was probably for flexibility with the borrow history but it means you can't do a clean JOIN.
- The analytics view rebuilds everything from scratch on each request. Adding caching would help if the book/student count grows significantly.
- There's no password reset flow for admin accounts. You'd have to use `python manage.py changepassword`.
- The `BorrowHistory.borrow_date` and `return_date` fields are used inconsistently across old and new records -- some older code paths set `return_date` at checkout time as a due date, and the `is_overdue()` method relies on that.

---

## Authors

Bright R. Bastasa - Former Student of Philippine Science High School under Project eTala