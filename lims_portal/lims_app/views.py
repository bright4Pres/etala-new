from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.shortcuts import render, redirect
from .models import Book, BookCopy, BorrowHistory, StudentActivation, grade_Seven, grade_Eight, grade_Nine, grade_Ten, grade_Eleven, grade_Twelve
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.db.models import Count, Q, Avg
from django.db import transaction, IntegrityError
from datetime import datetime, timedelta
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib import messages
from django.core.management import call_command
from io import StringIO
from django.conf import settings
from pathlib import Path
import shutil

@ensure_csrf_cookie
def home(request):
    return render(request, "home.html", context={"current_tab": "home"})

def about(request):
    return render(request, "about.html", context={"current_tab": "about"})

def books(request):
    authors = Book.objects.values_list('mainAuthor', flat=True).distinct()
    locations = BookCopy.objects.values_list('Location', flat=True).distinct()

    selected_author = request.GET.get('author')
    selected_location = request.GET.get('location')
    search_query = request.GET.get('search')

    books_query = Book.objects.all()
    if selected_author:
        books_query = books_query.filter(mainAuthor=selected_author)
    if selected_location:
        books_query = books_query.filter(copies__Location=selected_location).distinct()
    if search_query:
        books_query = books_query.filter(Title__icontains=search_query)

    return render(
        request,
        "books.html",
        context={
            "current_tab": "books",
            "books": books_query,
            "authors": authors,
            "locations": locations,
            "selected_author": selected_author,
            "selected_location": selected_location,
            "search_query": search_query,
        }
    )
def register_account(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        id_number = data.get('idNumber')
        email = data.get('email')
        batch = data.get('batch')

        # Check if student already exists in any grade
        for model in [grade_Seven, grade_Eight, grade_Nine, grade_Ten, grade_Eleven, grade_Twelve]:
            if model.objects.filter(school_id=id_number).exists():
                return JsonResponse({'error': 'ID Number already exists.'}, status=400)
            if model.objects.filter(name=name).exists():
                return JsonResponse({'error': 'Name already exists.'}, status=400)

        # Note: This function is no longer needed with the new OTP registration flow
        # Students are now created via CSV import and OTP activation
        return JsonResponse({'error': 'Please use the new registration flow with OTP verification.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def check_duplicate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id_number = data.get('idNumber')
        name = data.get('name')

        # Check if student exists in any grade
        duplicate = False
        for model in [grade_Seven, grade_Eight, grade_Nine, grade_Ten, grade_Eleven, grade_Twelve]:
            if model.objects.filter(school_id=id_number).exists() or model.objects.filter(name=name).exists():
                duplicate = True
                break
        
        return JsonResponse({'duplicate': duplicate})
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def records(request):
    # Capture user-selected filters
    book_type = request.GET.get('book_type')
    language = request.GET.get('language')
    publisher = request.GET.get('publisher')
    main_author = request.GET.get('main_author')
    co_author = request.GET.get('co_author')
    location = request.GET.get('location')
    search_query = request.GET.get('search')

    # Start with all books
    books_query = Book.objects.all()
    
    # Apply filters to books
    if book_type:
        books_query = books_query.filter(Type=book_type)
    if language:
        books_query = books_query.filter(Language=language)
    if publisher:
        books_query = books_query.filter(Publisher=publisher)
    if main_author:
        books_query = books_query.filter(mainAuthor=main_author)
    if co_author:
        books_query = books_query.filter(coAuthor=co_author)
    if search_query:
        books_query = books_query.filter(
            Q(Title__icontains=search_query) | 
            Q(mainAuthor__icontains=search_query) | 
            Q(coAuthor__icontains=search_query) |
            Q(callNumber__icontains=search_query) |
            Q(Publisher__icontains=search_query) |
            Q(Edition__icontains=search_query) |
            Q(Editors__icontains=search_query) |
            Q(placeofPublication__icontains=search_query) |
            Q(Language__icontains=search_query) |
            Q(Type__icontains=search_query) |
            Q(acquisitionStatus__icontains=search_query) |
            Q(copies__accessionNumber__icontains=search_query) |
            Q(copies__Location__icontains=search_query) |
            Q(copies__status__icontains=search_query) |
            Q(copies__borrowed_by__icontains=search_query)
        ).distinct()
    
    # If location filter, only include books that have copies in that location
    if location:
        books_query = books_query.filter(copies__Location=location).distinct()
    
    # Build grouped book data with copy information
    all_books = []
    for book in books_query.order_by('-id'):
        copies = book.copies.all()
        
        # If location filter is set, only include copies from that location
        if location:
            copies = copies.filter(Location=location)
        
        # Calculate availability
        total_copies = copies.count()
        available_copies = copies.filter(status='Available').count()
        
        all_books.append({
            'id': book.id,
            'Title': book.Title,
            'mainAuthor': book.mainAuthor,
            'coAuthor': book.coAuthor,
            'Publisher': book.Publisher,
            'Edition': book.Edition,
            'callNumber': book.callNumber,
            'Language': book.Language,
            'Type': book.Type,
            'placeofPublication': book.placeofPublication,
            'copyrightDate': str(book.copyrightDate) if book.copyrightDate else None,
            'publicationDate': str(book.publicationDate) if book.publicationDate else None,
            'Editors': book.Editors,
            'acquisitionStatus': book.acquisitionStatus,
            'total_copies': total_copies,
            'available_copies': available_copies,
            'borrowed_copies': total_copies - available_copies,
            'copies': [{
                'accessionNumber': c.accessionNumber,
                'Location': c.Location,
                'status': c.status,
                'borrowed_by': c.borrowed_by,
                'student_id': c.student_id,
                'borrow_date': str(c.borrow_date) if c.borrow_date else None,
                'return_date': str(c.return_date) if c.return_date else None
            } for c in copies]
        })

    # Get distinct values for filter options
    distinct_languages = Book.objects.values_list("Language", flat=True).distinct()
    distinct_publishers = Book.objects.values_list("Publisher", flat=True).distinct()
    distinct_authors = Book.objects.values_list("mainAuthor", flat=True).distinct()
    distinct_coauthors = Book.objects.values_list("coAuthor", flat=True).distinct().exclude(coAuthor__isnull=True)
    distinct_locations = BookCopy.objects.values_list("Location", flat=True).distinct()

    selected_filters = {
        "book_type": book_type,
        "language": language,
        "publisher": publisher,
        "main_author": main_author,
        "co_author": co_author,
        "location": location,
        "search": search_query,
    }

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"books": all_books})

    return render(request, "records.html", {
        "current_tab": "records",
        "recorded_books": all_books,
        "distinct_languages": distinct_languages,
        "distinct_publishers": distinct_publishers,
        "distinct_authors": distinct_authors,
        "distinct_coauthors": distinct_coauthors,
        "distinct_locations": distinct_locations,
        "selected_filters": selected_filters,
    })
    
def analytics(request):
    now = timezone.now()
    
    # ========== CORE METRICS ==========
    total_books_count = Book.objects.count()
    # Count all students across all grade models
    total_accounts = sum([
        grade_Seven.objects.count(),
        grade_Eight.objects.count(),
        grade_Nine.objects.count(),
        grade_Ten.objects.count(),
        grade_Eleven.objects.count(),
        grade_Twelve.objects.count(),
    ])
    total_borrows_all_time = BorrowHistory.objects.count()
    # count book copies marked as Borrowed in BookCopy.status
    currently_borrowed = BookCopy.objects.filter(status='Borrowed').count()
    available_books = BookCopy.objects.filter(status='Available').count()
    
    # Overdue books (borrow records not returned and past return_date)
    overdue_books = BorrowHistory.objects.filter(
        returned=False,
        return_date__lt=timezone.now()
    ).count()
    
    # ========== TIME-BASED FILTERS ==========
    period = request.GET.get('period', 'month')
    
    if period == 'day':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_label = "Today"
    elif period == 'week':
        start_date = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        period_label = "This Week"
    elif period == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_label = "This Month"
    elif period == 'quarter':
        quarter_month = ((now.month - 1) // 3) * 3 + 1
        start_date = now.replace(month=quarter_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        period_label = "This Quarter"
    elif period == 'year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        period_label = "This Year"
    else:
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_label = "This Month"
    
    # Period-specific metrics
    period_borrows = BorrowHistory.objects.filter(borrow_date__gte=start_date).count()
    period_returns = BorrowHistory.objects.filter(returned=True, return_date__gte=start_date).count()
    # Count new students from all grade models in period
    period_new_accounts = sum([
        grade_Seven.objects.filter(created_at__gte=start_date).count(),
        grade_Eight.objects.filter(created_at__gte=start_date).count(),
        grade_Nine.objects.filter(created_at__gte=start_date).count(),
        grade_Ten.objects.filter(created_at__gte=start_date).count(),
        grade_Eleven.objects.filter(created_at__gte=start_date).count(),
        grade_Twelve.objects.filter(created_at__gte=start_date).count(),
    ])
    
    # ========== MONTHLY BORROWS (Last 7 months) ==========
    def shift_month(year, month, delta):
        month += delta
        while month > 12:
            month -= 12
            year += 1
        while month < 1:
            month += 12
            year -= 1
        return year, month

    monthly_labels = []
    monthly_data = []
    months_back = 6
    for offset in range(months_back, -1, -1):
        y, m = shift_month(now.year, now.month, -offset)
        label = datetime(y, m, 1).strftime('%b %Y')
        count = BorrowHistory.objects.filter(borrow_date__year=y, borrow_date__month=m).count()
        monthly_labels.append(label)
        monthly_data.append(count)

    # ========== WEEKLY ACTIVITY (Last 7 days) ==========
    weekly_labels = []
    weekly_data = []
    for offset in range(6, -1, -1):
        day = now - timedelta(days=offset)
        label = day.strftime('%a %m/%d')
        count = BorrowHistory.objects.filter(borrow_date__date=day.date()).count()
        weekly_labels.append(label)
        weekly_data.append(count)

    # ========== BOOK TYPE DISTRIBUTION ==========
    type_qs = Book.objects.values('Type').annotate(count=Count('id')).order_by('-count')
    type_labels = [t['Type'] for t in type_qs]
    type_data = [t['count'] for t in type_qs]

    # ========== LANGUAGE DISTRIBUTION ==========
    language_qs = Book.objects.values('Language').annotate(count=Count('id')).order_by('-count')[:5]
    language_labels = [lang['Language'] for lang in language_qs]
    language_data = [lang['count'] for lang in language_qs]

    # ========== TOP BORROWERS & MOST BORROWED ==========
    top_borrowers = BorrowHistory.objects.values('accountName', 'accountID').annotate(borrow_count=Count('id')).order_by('-borrow_count')[:10]
    most_borrowed = BorrowHistory.objects.values('bookTitle', 'bookID').annotate(borrow_count=Count('id')).order_by('-borrow_count')[:10]

    # ========== LOCATION STATISTICS ==========
    location_stats = BookCopy.objects.values('Location').annotate(
        total=Count('id'),
        borrowed=Count('id', filter=Q(status='Borrowed')),
        available=Count('id', filter=Q(status='Available'))
    ).order_by('-total')

    # ========== GENDER STATISTICS ==========
    # Overall gender proportions
    overall_gender = {
        'Male': sum([
            grade_Seven.objects.filter(gender='Male').count(),
            grade_Eight.objects.filter(gender='Male').count(),
            grade_Nine.objects.filter(gender='Male').count(),
            grade_Ten.objects.filter(gender='Male').count(),
            grade_Eleven.objects.filter(gender='Male').count(),
            grade_Twelve.objects.filter(gender='Male').count(),
        ]),
        'Female': sum([
            grade_Seven.objects.filter(gender='Female').count(),
            grade_Eight.objects.filter(gender='Female').count(),
            grade_Nine.objects.filter(gender='Female').count(),
            grade_Ten.objects.filter(gender='Female').count(),
            grade_Eleven.objects.filter(gender='Female').count(),
            grade_Twelve.objects.filter(gender='Female').count(),
        ]),
        'Other': sum([
            grade_Seven.objects.filter(gender='Other').count(),
            grade_Eight.objects.filter(gender='Other').count(),
            grade_Nine.objects.filter(gender='Other').count(),
            grade_Ten.objects.filter(gender='Other').count(),
            grade_Eleven.objects.filter(gender='Other').count(),
            grade_Twelve.objects.filter(gender='Other').count(),
        ]),
    }
    total_students = sum(overall_gender.values())
    overall_gender_proportions = {k: round((v / total_students * 100), 1) if total_students > 0 else 0 for k, v in overall_gender.items()}

    # Pie chart data
    overall_gender_labels = []
    overall_gender_data = []
    for label, value in overall_gender_proportions.items():
        if value > 0:
            overall_gender_labels.append(label)
            overall_gender_data.append(value)

    # Gender proportions per batch
    batch_gender_stats = {
        'Grade 7': {
            'Male': grade_Seven.objects.filter(gender='Male').count(),
            'Female': grade_Seven.objects.filter(gender='Female').count(),
            'Other': grade_Seven.objects.filter(gender='Other').count(),
        },
        'Grade 8': {
            'Male': grade_Eight.objects.filter(gender='Male').count(),
            'Female': grade_Eight.objects.filter(gender='Female').count(),
            'Other': grade_Eight.objects.filter(gender='Other').count(),
        },
        'Grade 9': {
            'Male': grade_Nine.objects.filter(gender='Male').count(),
            'Female': grade_Nine.objects.filter(gender='Female').count(),
            'Other': grade_Nine.objects.filter(gender='Other').count(),
        },
        'Grade 10': {
            'Male': grade_Ten.objects.filter(gender='Male').count(),
            'Female': grade_Ten.objects.filter(gender='Female').count(),
            'Other': grade_Ten.objects.filter(gender='Other').count(),
        },
        'Grade 11': {
            'Male': grade_Eleven.objects.filter(gender='Male').count(),
            'Female': grade_Eleven.objects.filter(gender='Female').count(),
            'Other': grade_Eleven.objects.filter(gender='Other').count(),
        },
        'Grade 12': {
            'Male': grade_Twelve.objects.filter(gender='Male').count(),
            'Female': grade_Twelve.objects.filter(gender='Female').count(),
            'Other': grade_Twelve.objects.filter(gender='Other').count(),
        },
    }
    for batch, genders in batch_gender_stats.items():
        # Only include the gender keys (Male, Female, Other) - not 'total' or 'proportions'
        gender_counts = {k: v for k, v in genders.items() if k in ['Male', 'Female', 'Other']}
        total = sum(gender_counts.values())
        batch_gender_stats[batch]['total'] = total
        batch_gender_stats[batch]['proportions'] = {k: round((v / total * 100), 1) if total > 0 else 0 for k, v in gender_counts.items()}

    # Pie chart data for batches
    batch_gender_pie_data = {}
    for batch, stats in batch_gender_stats.items():
        filtered_labels = []
        filtered_data = []
        for label, value in stats['proportions'].items():
            if value > 0:
                filtered_labels.append(label)
                filtered_data.append(value)
        batch_gender_pie_data[batch] = {
            'labels': filtered_labels,
            'data': filtered_data
        }

    # Batch activity (borrows per batch)
    batch_activity = {
        'Grade 7': BorrowHistory.objects.filter(accountID__in=grade_Seven.objects.values('school_id')).count(),
        'Grade 8': BorrowHistory.objects.filter(accountID__in=grade_Eight.objects.values('school_id')).count(),
        'Grade 9': BorrowHistory.objects.filter(accountID__in=grade_Nine.objects.values('school_id')).count(),
        'Grade 10': BorrowHistory.objects.filter(accountID__in=grade_Ten.objects.values('school_id')).count(),
        'Grade 11': BorrowHistory.objects.filter(accountID__in=grade_Eleven.objects.values('school_id')).count(),
        'Grade 12': BorrowHistory.objects.filter(accountID__in=grade_Twelve.objects.values('school_id')).count(),
    }
    # Sort batch_activity by borrow count descending
    sorted_batch_activity = []
    for batch, count in sorted(batch_activity.items(), key=lambda x: x[1], reverse=True):
        sorted_batch_activity.append({
            'batch': batch,
            'borrows': count,
            'gender_proportions': batch_gender_stats[batch]['proportions'],
            'total_students': batch_gender_stats[batch]['total']
        })

    # ========== BATCH STATISTICS ==========
    # Batch statistics removed as Account model no longer exists
    batch_stats = []

    # ========== RECENT ACTIVITY & OVERDUE DETAILS ==========
    recent_activity = BorrowHistory.objects.select_related().order_by('-borrow_date')[:15]
    overdue_list = BorrowHistory.objects.filter(returned=False, return_date__lt=timezone.now()).order_by('return_date')[:10]

    # ========== RETURN RATE CALCULATION ==========
    returned_count = BorrowHistory.objects.filter(returned=True).count()
    return_rate = (returned_count / total_borrows_all_time * 100) if total_borrows_all_time > 0 else 0.0

    # ========== AVERAGE BORROW DURATION ==========
    completed_borrows = BorrowHistory.objects.filter(returned=True, return_date__isnull=False)
    if completed_borrows.exists():
        total_duration = sum([
            (b.return_date - b.borrow_date).days
            for b in completed_borrows
            if b.return_date and b.borrow_date
        ])
        avg_borrow_days = total_duration / completed_borrows.count()
    else:
        avg_borrow_days = 0.0

    # ========== PERCENTAGES FOR UI (avoid template math) ==========
    utilization_percent = int(currently_borrowed / total_books_count * 100) if total_books_count > 0 else 0
    avg_borrow_percent = int(min((avg_borrow_days / 14) * 100, 100))  # relative to a 14-day baseline
    return_rate_rounded = round(return_rate, 1)

    # ========== CALENDAR HEATMAP DATA (Configurable Range & Navigation) ==========
    heatmap_range = request.GET.get('heatmap_range', 'year')  # 'week', 'month', 'year'
    heatmap_offset = int(request.GET.get('heatmap_offset', 0))
    today = now.date()

    if heatmap_range == 'week':
        days = 7
        period_label = 'This Week'
        start_date = today - timedelta(days=(today.weekday() + 7 * heatmap_offset))
        end_date = start_date + timedelta(days=6)
    elif heatmap_range == 'month':
        # Go back N months
        month = today.month - heatmap_offset
        year = today.year
        while month < 1:
            month += 12
            year -= 1
        start_date = datetime(year, month, 1).date()
        # End of month
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
        days = (end_date - start_date).days + 1
        period_label = start_date.strftime('%B %Y')
    else:  # 'year' or default
        # Go back N years
        year = today.year - heatmap_offset
        start_date = datetime(year, 1, 1).date()
        end_date = datetime(year, 12, 31).date()
        days = (end_date - start_date).days + 1
        period_label = str(year)

    # Build heatmap data for the selected period
    heatmap_data = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        count = BorrowHistory.objects.filter(borrow_date__date=date).count()
        heatmap_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })

    # Navigation helpers
    prev_offset = heatmap_offset + 1
    next_offset = heatmap_offset - 1 if heatmap_offset > 0 else 0
    can_go_next = heatmap_offset > 0

    # ========== PACKAGE METRICS JSON ==========
    metrics = {
        "monthlyLabels": monthly_labels,
        "monthlyData": monthly_data,
        "weeklyLabels": weekly_labels,
        "weeklyData": weekly_data,
        "typeLabels": type_labels,
        "typeData": type_data,
        "languageLabels": language_labels,
        "languageData": language_data,
        "periodLabel": period_label,
        "heatmapData": heatmap_data,
        "heatmapRange": heatmap_range,
        "heatmapOffset": heatmap_offset,
        "heatmapPeriodLabel": period_label,
        "heatmapCanGoNext": can_go_next,
    }

    context = {
        "current_tab": "analytics",
        # Core counts
        "total_books_count": total_books_count,
        "total_accounts": total_accounts,
        "total_borrows_all_time": total_borrows_all_time,
        "currently_borrowed": currently_borrowed,
        "available_books": available_books,
        "overdue_books": overdue_books,

        # Percent / UI helpers
        "utilization_percent": utilization_percent,
        "avg_borrow_percent": avg_borrow_percent,
        "return_rate": return_rate_rounded,

        # Period-specific
        "period_borrows": period_borrows,
        "period_returns": period_returns,
        "period_new_accounts": period_new_accounts,
        "period_label": period_label,

        # Lists / details
        "top_borrowers": list(top_borrowers),
        "most_borrowed": list(most_borrowed),
        "location_stats": list(location_stats),
        "batch_stats": list(batch_stats),

        # Gender statistics
        "overall_gender_proportions": overall_gender_proportions,
        "overall_gender_labels": overall_gender_labels,
        "overall_gender_data": overall_gender_data,
        "batch_gender_stats": batch_gender_stats,
        "batch_gender_pie_data": batch_gender_pie_data,
        "sorted_batch_activity": sorted_batch_activity,

        # Recent activity & overdue
        "borrowed_books": recent_activity,
        "overdue_list": overdue_list,

        # Chart data
        "metrics_json": json.dumps(metrics),
        "heatmap_range": heatmap_range,
        "heatmap_offset": heatmap_offset,
        "heatmap_period_label": period_label,
        "heatmap_can_go_next": can_go_next,
        "heatmap_prev_offset": prev_offset,
        "heatmap_next_offset": next_offset,
    }

    return render(request, "analytics.html", context)


# Admin Views
def admin_login(request):
    if request.method == 'POST':
        # Rate limiting: block after 5 failed attempts for 15 minutes
        ip = request.META.get('REMOTE_ADDR', '')
        rate_key = f'login_attempts_{ip}'
        attempts = cache.get(rate_key, 0)
        if attempts >= 5:
            messages.error(request, 'Too many failed login attempts. Please try again in 15 minutes.')
            return render(request, 'admin_login.html')

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            cache.delete(rate_key)  # Reset on successful login
            login(request, user)
            return redirect('admin_dashboard')
        else:
            cache.set(rate_key, attempts + 1, 900)  # 15 min lockout
            messages.error(request, 'Invalid credentials or not authorized.')
    return render(request, 'admin_login.html')

@staff_member_required
def admin_logout(request):
    logout(request)
    return redirect('admin_login')

@staff_member_required
def admin_dashboard(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'checkout':
            accession_number = request.POST.get('book_id', '').strip()
            student_id = request.POST.get('student_id', '').strip()
            try:
                # Find the book copy by accession number
                book_copy = BookCopy.objects.get(accessionNumber=accession_number)
                if book_copy.status != 'Available':
                    messages.error(request, f'Book "{book_copy.book.Title}" is not available for checkout.')
                else:
                    # Create borrow history
                    borrow = BorrowHistory(
                        book_copy=book_copy,
                        bookID=accession_number,  # Keep for backward compatibility
                        accountID=student_id,
                        bookTitle=book_copy.book.Title,
                        accountName=student_id  # Could look up student name here
                    )
                    borrow.save()
                    
                    # Update book copy status
                    book_copy.status = 'Borrowed'
                    book_copy.borrowed_by = student_id
                    book_copy.student_id = student_id
                    book_copy.borrow_date = timezone.now()
                    book_copy.save()
                    
                    messages.success(request, f'Book "{book_copy.book.Title}" (#{accession_number}) checked out to student {student_id}.')
            except BookCopy.DoesNotExist:
                messages.error(request, f'Book copy with accession number {accession_number} not found.')
            except Exception as e:
                messages.error(request, f'Error checking out book: {str(e)}')
                
        elif action == 'return':
            borrow_id = request.POST.get('borrow_id')
            try:
                borrow = BorrowHistory.objects.get(id=borrow_id, returned=False)
                borrow.returned = True
                borrow.return_date = timezone.now()
                borrow.save()
                
                # Update book copy status
                book_copy = borrow.book_copy
                book_copy.status = 'Available'
                book_copy.borrowed_by = None
                book_copy.student_id = None
                book_copy.borrow_date = None
                book_copy.return_date = None
                book_copy.save()
                
                messages.success(request, 'Book returned successfully.')
            except BorrowHistory.DoesNotExist:
                messages.error(request, 'Borrow record not found.')
            except Exception as e:
                messages.error(request, str(e))
        
        elif action == 'return_barcode':
            accession_number = request.POST.get('accession_number', '').strip()
            try:
                # Find the book copy
                book_copy = BookCopy.objects.get(accessionNumber=accession_number)
                
                # Find the active borrow record for this copy
                borrow = BorrowHistory.objects.get(book_copy=book_copy, returned=False)
                borrow.returned = True
                borrow.return_date = timezone.now()
                borrow.save()
                
                # Update book copy status
                book_copy.status = 'Available'
                book_copy.borrowed_by = None
                book_copy.student_id = None
                book_copy.borrow_date = None
                book_copy.return_date = None
                book_copy.save()
                
                messages.success(request, f'Book "{book_copy.book.Title}" (#{accession_number}) returned successfully.')
            except BookCopy.DoesNotExist:
                messages.error(request, f'Book copy with accession number {accession_number} not found.')
            except BorrowHistory.DoesNotExist:
                messages.error(request, f'No active borrow record found for accession number: {accession_number}')
            except Exception as e:
                messages.error(request, f'Error returning book: {str(e)}')
        
        elif action == 'edit_book':
            book_id = request.POST.get('book_id')
            try:
                book = Book.objects.get(id=book_id)
                book.Title = request.POST.get('title', book.Title)
                book.mainAuthor = request.POST.get('main_author', book.mainAuthor)
                book.coAuthor = request.POST.get('co_author', book.coAuthor)
                book.Publisher = request.POST.get('publisher', book.Publisher)
                book.Edition = request.POST.get('edition', book.Edition)
                book.callNumber = request.POST.get('call_number', book.callNumber)
                book.Language = request.POST.get('language', book.Language)
                book.Type = request.POST.get('type', book.Type)
                book.save()

                # Update copies (status/location) from modal, if present
                copy_ids = request.POST.getlist('copy_id')
                copy_statuses = request.POST.getlist('copy_status')
                copy_locations = request.POST.getlist('copy_location')

                if copy_ids:
                    allowed_status = {'Available', 'Unavailable', 'Borrowed', 'Lost'}
                    for i, copy_id in enumerate(copy_ids):
                        status = copy_statuses[i] if i < len(copy_statuses) else 'Available'
                        location = copy_locations[i] if i < len(copy_locations) else ''
                        if status not in allowed_status:
                            status = 'Available'
                        BookCopy.objects.filter(id=copy_id, book=book).update(
                            status=status,
                            Location=(location or '').strip(),
                        )

                messages.success(request, f'Book "{book.Title}" updated successfully.')
            except Book.DoesNotExist:
                messages.error(request, 'Book not found.')
            except Exception as e:
                messages.error(request, f'Error updating book: {str(e)}')

        elif action == 'delete_copy':
            confirm_delete = request.POST.get('confirm_delete', 'no')
            copy_id = request.POST.get('copy_id')
            if confirm_delete != 'yes':
                messages.error(request, 'Delete not confirmed.')
                return redirect('admin_dashboard')
            try:
                copy = BookCopy.objects.select_related('book').get(id=copy_id)
                accession = copy.accessionNumber
                title = copy.book.Title
                copy.delete()
                messages.success(request, f'Copy {accession} removed from "{title}".')
            except BookCopy.DoesNotExist:
                messages.error(request, 'Copy not found.')
            except Exception as e:
                messages.error(request, f'Error deleting copy: {str(e)}')
        
        elif action == 'edit_user':
            # New modal fields
            old_school_id = (request.POST.get('old_school_id') or '').strip()
            old_grade_num = (request.POST.get('old_grade_num') or '').strip()
            new_school_id = (request.POST.get('school_id') or '').strip()
            new_grade_num = (request.POST.get('grade_num') or '').strip()
            
            # Backward compatibility with the old modal
            if not old_school_id:
                old_school_id = new_school_id
            if not old_grade_num:
                grade_str = (request.POST.get('grade') or '').strip().lower()
                if '7' in grade_str or 'seven' in grade_str:
                    old_grade_num = '7'
                elif '8' in grade_str or 'eight' in grade_str:
                    old_grade_num = '8'
                elif '9' in grade_str or 'nine' in grade_str:
                    old_grade_num = '9'
                elif '10' in grade_str or 'ten' in grade_str:
                    old_grade_num = '10'
                elif '11' in grade_str or 'eleven' in grade_str:
                    old_grade_num = '11'
                elif '12' in grade_str or 'twelve' in grade_str:
                    old_grade_num = '12'
            if not new_grade_num:
                new_grade_num = old_grade_num

            name = (request.POST.get('name') or '').strip()
            email = (request.POST.get('email') or '').strip()
            batch = (request.POST.get('batch') or '').strip() or None
            is_activated = (request.POST.get('is_activated', 'false').lower() == 'true')

            grade_map = {
                '7': grade_Seven,
                '8': grade_Eight,
                '9': grade_Nine,
                '10': grade_Ten,
                '11': grade_Eleven,
                '12': grade_Twelve,
            }
            source_model = grade_map.get(old_grade_num)
            target_model = grade_map.get(new_grade_num)
            if not source_model or not target_model:
                messages.error(request, 'Invalid grade.')
                return redirect('admin_dashboard')

            try:
                with transaction.atomic():
                    user = source_model.objects.get(school_id=old_school_id)

                    # Unique school_id across all grade tables
                    if new_school_id != old_school_id:
                        for model in [grade_Seven, grade_Eight, grade_Nine, grade_Ten, grade_Eleven, grade_Twelve]:
                            if model is source_model:
                                continue
                            if model.objects.filter(school_id=new_school_id).exists():
                                messages.error(request, 'School ID already exists.')
                                return redirect('admin_dashboard')

                    # If moving grade, ensure name is not already used in the target table
                    new_name = name or user.name
                    if target_model is not source_model:
                        if target_model.objects.filter(name=new_name).exists():
                            messages.error(request, 'Name already exists in the selected grade.')
                            return redirect('admin_dashboard')

                    if target_model is source_model:
                        user.school_id = new_school_id or user.school_id
                        user.name = new_name
                        user.email = email or user.email
                        user.batch = batch
                        user.is_activated = is_activated
                        user.save()
                    else:
                        target_model.objects.create(
                            name=new_name,
                            school_id=new_school_id or user.school_id,
                            gender=user.gender,
                            email=email or user.email,
                            batch=batch,
                            is_activated=is_activated,
                        )
                        user.delete()

                    # Keep StudentActivation in sync if present
                    StudentActivation.objects.filter(school_id=old_school_id).update(
                        school_id=new_school_id or old_school_id,
                        name=new_name,
                        email=email or user.email,
                        batch=(batch or None),
                        grade=int(new_grade_num) if str(new_grade_num).isdigit() else int(old_grade_num),
                        is_activated=is_activated,
                    )

                messages.success(request, 'User updated successfully.')
            except source_model.DoesNotExist:
                messages.error(request, 'User not found.')
            except IntegrityError:
                messages.error(request, 'Could not update user. Ensure Name and School ID are unique.')
            except Exception as e:
                messages.error(request, f'Error updating user: {str(e)}')

        elif action == 'delete_user':
            confirm_delete = request.POST.get('confirm_delete', 'no')
            school_id = (request.POST.get('school_id') or '').strip()
            grade_num = (request.POST.get('grade_num') or '').strip()
            if confirm_delete != 'yes':
                messages.error(request, 'Delete not confirmed.')
                return redirect('admin_dashboard')

            grade_map = {
                '7': grade_Seven,
                '8': grade_Eight,
                '9': grade_Nine,
                '10': grade_Ten,
                '11': grade_Eleven,
                '12': grade_Twelve,
            }
            model = grade_map.get(grade_num)
            if not model:
                messages.error(request, 'Invalid grade.')
                return redirect('admin_dashboard')

            try:
                with transaction.atomic():
                    user = model.objects.get(school_id=school_id)
                    name = user.name
                    user.delete()
                    StudentActivation.objects.filter(school_id=school_id).delete()
                messages.success(request, f'User "{name}" deleted.')
            except model.DoesNotExist:
                messages.error(request, 'User not found.')
            except Exception as e:
                messages.error(request, f'Error deleting user: {str(e)}')

        elif action == 'move_up':
            password = request.POST.get('password', '')
            if not request.user.check_password(password):
                messages.error(request, 'Password verification failed.')
                return redirect('admin_dashboard')
            try:
                output = StringIO()
                call_command('moveup_students', stdout=output)
                messages.success(request, 'Move-up complete.')
            except Exception as e:
                messages.error(request, f'Error during move-up: {str(e)}')

        elif action == 'create_backup':
            try:
                backups_dir = Path(settings.BASE_DIR) / 'backups'
                backups_dir.mkdir(parents=True, exist_ok=True)
                ts = timezone.now().strftime('%Y%m%d_%H%M%S')
                run_dir = backups_dir / ts
                run_dir.mkdir(parents=True, exist_ok=True)

                db_path = Path(settings.BASE_DIR) / 'db.sqlite3'
                if db_path.exists():
                    shutil.copy2(db_path, run_dir / 'db.sqlite3')

                books_data = list(Book.objects.all().values())
                copies_data = list(BookCopy.objects.all().values())
                (run_dir / 'books.json').write_text(json.dumps(books_data, default=str, indent=2), encoding='utf-8')
                (run_dir / 'book_copies.json').write_text(json.dumps(copies_data, default=str, indent=2), encoding='utf-8')

                users = {
                    'grade7': list(grade_Seven.objects.all().values()),
                    'grade8': list(grade_Eight.objects.all().values()),
                    'grade9': list(grade_Nine.objects.all().values()),
                    'grade10': list(grade_Ten.objects.all().values()),
                    'grade11': list(grade_Eleven.objects.all().values()),
                    'grade12': list(grade_Twelve.objects.all().values()),
                }
                (run_dir / 'users.json').write_text(json.dumps(users, default=str, indent=2), encoding='utf-8')
                (run_dir / 'grade12_graduating.json').write_text(json.dumps(users['grade12'], default=str, indent=2), encoding='utf-8')

                messages.success(request, f'Backup created: {run_dir.name}')
            except Exception as e:
                messages.error(request, f'Backup failed: {str(e)}')

        elif action == 'add_book':
            title = request.POST.get('title', '').strip()
            main_author = request.POST.get('main_author', '').strip()
            co_author = request.POST.get('co_author', '').strip()
            publisher = request.POST.get('publisher', '').strip()
            edition = request.POST.get('edition', '').strip()
            call_number = request.POST.get('call_number', '').strip()
            language = request.POST.get('language', '').strip() or 'English'
            book_type = request.POST.get('type', '').strip() or 'Other'

            copies_raw = request.POST.get('copies_list', '').strip()

            if not title or not main_author or not call_number:
                messages.error(request, 'Title, Main Author, and Call Number are required.')
                return redirect('admin_dashboard')

            if not copies_raw:
                messages.error(request, 'Please provide at least one copy (accession number, location, status).')
                return redirect('admin_dashboard')

            allowed_status = {'Available', 'Unavailable', 'Borrowed', 'Lost'}
            copies_to_create = []
            for line in copies_raw.splitlines():
                line = line.strip()
                if not line:
                    continue

                # Accept: ACC,Location,Status  OR  ACC | Location | Status
                parts = [p.strip() for p in (line.split('|') if '|' in line else line.split(','))]
                parts = [p for p in parts if p]
                if len(parts) < 2:
                    messages.error(request, f'Invalid copy line: "{line}". Use "ACC, Location, Status".')
                    return redirect('admin_dashboard')

                accession = parts[0]
                location = parts[1]
                status = parts[2] if len(parts) >= 3 else 'Available'
                if status not in allowed_status:
                    status = 'Available'

                copies_to_create.append((accession, location, status))

            if not copies_to_create:
                messages.error(request, 'No valid copy lines found.')
                return redirect('admin_dashboard')

            try:
                with transaction.atomic():
                    # One Book per call number; copies are BookCopy rows.
                    book, created = Book.objects.get_or_create(
                        callNumber=call_number,
                        defaults={
                            'Title': title,
                            'mainAuthor': main_author,
                            'coAuthor': co_author or None,
                            'Publisher': publisher or None,
                            'Edition': edition or None,
                            'Language': language,
                            'Type': book_type,
                        }
                    )

                    if not created:
                        # Update core fields (keep it simple: overwrite with provided non-empty values)
                        book.Title = title or book.Title
                        book.mainAuthor = main_author or book.mainAuthor
                        book.coAuthor = co_author or book.coAuthor
                        book.Publisher = publisher or book.Publisher
                        book.Edition = edition or book.Edition
                        book.Language = language or book.Language
                        book.Type = book_type or book.Type
                        book.save()

                    for accession, location, status in copies_to_create:
                        BookCopy.objects.create(
                            book=book,
                            accessionNumber=accession,
                            Location=location,
                            status=status,
                        )

                messages.success(request, f'Book "{title}" saved and {len(copies_to_create)} copy/copies added.')
            except IntegrityError:
                messages.error(request, 'Could not save book/copies. Accession numbers and call numbers must be unique.')
            except Exception as e:
                messages.error(request, f'Error adding book: {str(e)}')

        elif action == 'add_user':
            grade_num = request.POST.get('grade_num', '').strip()
            name = request.POST.get('name', '').strip()
            school_id = request.POST.get('school_id', '').strip()
            email = request.POST.get('email', '').strip()
            batch = request.POST.get('batch', '').strip()
            gender = request.POST.get('gender', 'Other').strip() or 'Other'
            is_activated = request.POST.get('is_activated', 'false').lower() == 'true'

            if not grade_num or not name or not school_id or not email:
                messages.error(request, 'Grade, Name, School ID, and Email are required.')
                return redirect('admin_dashboard')

            grade_model = {
                '7': grade_Seven,
                '8': grade_Eight,
                '9': grade_Nine,
                '10': grade_Ten,
                '11': grade_Eleven,
                '12': grade_Twelve,
            }.get(grade_num)

            if not grade_model:
                messages.error(request, 'Invalid grade selected.')
                return redirect('admin_dashboard')

            # Prevent duplicate school IDs across all grades
            for model in [grade_Seven, grade_Eight, grade_Nine, grade_Ten, grade_Eleven, grade_Twelve]:
                if model.objects.filter(school_id=school_id).exists():
                    messages.error(request, 'School ID already exists.')
                    return redirect('admin_dashboard')

            try:
                grade_model.objects.create(
                    name=name,
                    school_id=school_id,
                    email=email,
                    batch=batch or None,
                    gender=gender,
                    is_activated=is_activated,
                )
                messages.success(request, f'User "{name}" added successfully.')
            except IntegrityError:
                messages.error(request, 'Could not add user. Name and School ID must be unique.')
            except Exception as e:
                messages.error(request, f'Error adding user: {str(e)}')
        
        return redirect('admin_dashboard')
    
    borrowed_books = BorrowHistory.objects.filter(returned=False).select_related()
    overdue_books = [b for b in borrowed_books if b.is_overdue()]
    available_books_count = BookCopy.objects.filter(status='Available').count()
    available_book_copies = BookCopy.objects.filter(status='Available').select_related('book')
    recent_activity = BorrowHistory.objects.all().order_by('-borrow_date')[:10]
    
    # Get total books and book copies
    total_books_count = Book.objects.count()
    total_copies_count = BookCopy.objects.count()
    # Get all books with their copies information
    all_books = []
    for book in Book.objects.all().order_by('-id')[:50]:
        copies = book.copies.all()
        copies_payload = [
            {
                'id': c.id,
                'accessionNumber': c.accessionNumber,
                'status': c.status,
                'Location': c.Location,
                'borrowed_by': c.borrowed_by,
                'student_id': c.student_id,
            }
            for c in copies
        ]
        all_books.append({
            'id': book.id,
            'Title': book.Title,
            'mainAuthor': book.mainAuthor,
            'coAuthor': book.coAuthor,
            'Publisher': book.Publisher,
            'Edition': book.Edition,
            'callNumber': book.callNumber,
            'Language': book.Language,
            'Type': book.Type,
            'total_copies': book.get_total_copies(),
            'available_copies': book.get_available_copies(),
            'borrowed_copies': book.get_borrowed_copies(),
            'copies': copies_payload,
            'copies_json': json.dumps(copies_payload),
        })
    
    # Get all users from all grade models
    all_users = []
    grade_models = [
        (7, grade_Seven),
        (8, grade_Eight),
        (9, grade_Nine),
        (10, grade_Ten),
        (11, grade_Eleven),
        (12, grade_Twelve),
    ]
    for grade_num, model in grade_models:
        for user in model.objects.all()[:20]:  # Get up to 20 from each grade
            all_users.append({
                'name': user.name,
                'school_id': user.school_id,
                'email': user.email,
                'grade': f'Grade {grade_num}',
                'grade_num': grade_num,
                'batch': getattr(user, 'batch', 'N/A'),
                'is_activated': user.is_activated,
            })
    
    total_users_count = (
        grade_Seven.objects.count() + 
        grade_Eight.objects.count() + 
        grade_Nine.objects.count() + 
        grade_Ten.objects.count() + 
        grade_Eleven.objects.count() + 
        grade_Twelve.objects.count()
    )
    
    return render(request, 'cadmin.html', {
        'borrowed_books': borrowed_books,
        'overdue_books': overdue_books,
        'available_books_count': available_books_count,
        'available_books': available_book_copies,
        'recent_activity': recent_activity,
        'total_books_count': total_books_count,
        'total_copies_count': total_copies_count,
        'all_books': all_books,
        'total_users_count': total_users_count,
        'all_users': all_users,
    })

@staff_member_required
@require_http_methods(["GET", "POST"])
def admin_checkout(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        student_id = request.POST.get('student_id')
        try:
            borrow = BorrowHistory(bookID=book_id, accountID=student_id)
            borrow.save()
            messages.success(request, 'Book checked out successfully.')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, str(e))
    book_copies = BookCopy.objects.filter(status='Available').select_related('book')
    return render(request, 'admin_checkout.html', {'books': book_copies})

@staff_member_required
@require_http_methods(["GET", "POST"])
def admin_return(request):
    if request.method == 'POST':
        borrow_id = request.POST.get('borrow_id')
        try:
            borrow = BorrowHistory.objects.get(id=borrow_id, returned=False)
            borrow.returned = True
            borrow.return_date = timezone.now()
            borrow.save()
            
            # Update book copy status
            if borrow.book_copy:
                book_copy = borrow.book_copy
                book_copy.status = 'Available'
                book_copy.borrowed_by = None
                book_copy.student_id = None
                book_copy.borrow_date = None
                book_copy.return_date = None
                book_copy.save()
            else:
                # Fallback for legacy records without book_copy
                try:
                    book_copy = BookCopy.objects.get(accessionNumber=borrow.bookID)
                    book_copy.status = 'Available'
                    book_copy.borrowed_by = None
                    book_copy.student_id = None
                    book_copy.borrow_date = None
                    book_copy.return_date = None
                    book_copy.save()
                except BookCopy.DoesNotExist:
                    pass
            
            messages.success(request, 'Book returned successfully.')
        except BorrowHistory.DoesNotExist:
            messages.error(request, 'Borrow record not found.')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('admin_dashboard')
    borrowed_books = BorrowHistory.objects.filter(returned=False)
    return render(request, 'admin_return.html', {'borrowed_books': borrowed_books})

@staff_member_required
def admin_accounts(request):
    # Get all students grouped by grade
    all_students = {}
    for grade_num, model in [(7, grade_Seven), (8, grade_Eight), (9, grade_Nine), 
                              (10, grade_Ten), (11, grade_Eleven), (12, grade_Twelve)]:
        students = model.objects.all()
        all_students[grade_num] = students
    return render(request, 'admin_accounts.html', {'all_students': all_students})

@staff_member_required
def admin_books(request):
    search_query = request.GET.get('search', '')
    books = Book.objects.all()
    if search_query:
        books = books.filter(
            Q(Title__icontains=search_query) | 
            Q(callNumber__icontains=search_query) |
            Q(mainAuthor__icontains=search_query)
        )
    return render(request, 'admin_books.html', {'books': books, 'search_query': search_query})

@staff_member_required
def admin_edit_book(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        messages.error(request, 'Book not found.')
        return redirect('admin_books')
    if request.method == 'POST':
        book.Title = request.POST.get('Title')
        book.mainAuthor = request.POST.get('mainAuthor')
        book.coAuthor = request.POST.get('coAuthor', '')
        book.Publisher = request.POST.get('Publisher', '')
        book.Edition = request.POST.get('Edition', '')
        book.callNumber = request.POST.get('callNumber', '')
        book.Language = request.POST.get('Language', '')
        book.Type = request.POST.get('Type', '')
        book.save()
        messages.success(request, 'Book updated successfully.')
        return redirect('admin_books')
    return render(request, 'admin_edit_book.html', {'book': book})