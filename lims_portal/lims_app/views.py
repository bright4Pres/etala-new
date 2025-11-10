from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.shortcuts import render
from .models import Book, Account, BorrowHistory
from django.views.decorators.csrf import csrf_protect
from django.db.models import Count, Q, Avg
from datetime import datetime, timedelta
import json

def home(request):
    return render(request, "home.html", context={"current_tab": "home"})

def about(request):
    return render(request, "about.html", context={"current_tab": "about"})

def books(request):
    authors = Book.objects.values_list('mainAuthor', flat=True).distinct()
    locations = Book.objects.values_list('Location', flat=True).distinct()

    selected_author = request.GET.get('author')
    selected_location = request.GET.get('location')
    search_query = request.GET.get('search')

    books_query = Book.objects.filter(is_borrowed=False)
    if selected_author:
        books_query = books_query.filter(mainAuthor=selected_author)
    if selected_location:
        books_query = books_query.filter(Location=selected_location)
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

        if Account.objects.filter(school_id=id_number).exists():
            return JsonResponse({'error': 'ID Number already exists.'}, status=400)
        if Account.objects.filter(name=name).exists():
            return JsonResponse({'error': 'Name already exists.'}, status=400)

        if name and id_number and email and batch:
            Account.objects.create(
                name=name,
                school_id=id_number,
                email=email,
                batch=batch
            )
            return JsonResponse({'message': 'Account registered successfully!'})
        else:
            return JsonResponse({'error': 'Invalid data provided.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def check_duplicate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id_number = data.get('idNumber')
        name = data.get('name')

        duplicate = Account.objects.filter(school_id=id_number).exists() or Account.objects.filter(name=name).exists()
        return JsonResponse({'duplicate': duplicate})
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def records(request):
    all_books = Book.objects.all()

    # Capture user-selected filters
    book_type = request.GET.get('book_type')
    language = request.GET.get('language')
    publisher = request.GET.get('publisher')
    main_author = request.GET.get('main_author')
    co_author = request.GET.get('co_author')
    location = request.GET.get('location')

    # Apply filters dynamically
    if book_type:
        all_books = all_books.filter(Type=book_type)
    if language:
        all_books = all_books.filter(Language=language)
    if publisher:
        all_books = all_books.filter(Publisher=publisher)
    if main_author:
        all_books = all_books.filter(mainAuthor=main_author)
    if co_author:
        all_books = all_books.filter(coAuthor=co_author)
    if location:
        all_books = all_books.filter(Location=location)

    # values based on filtered queryset
    distinct_languages = all_books.values_list("Language", flat=True).distinct()
    distinct_publishers = all_books.values_list("Publisher", flat=True).distinct()
    distinct_authors = all_books.values_list("mainAuthor", flat=True).distinct()
    distinct_coauthors = all_books.values_list("coAuthor", flat=True).distinct()
    distinct_locations = all_books.values_list("Location", flat=True).distinct()

    selected_filters = {
        "book_type": book_type,
        "language": language,
        "publisher": publisher,
        "main_author": main_author,
        "co_author": co_author,
        "location": location,
    }

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        books_data = list(all_books.values("Title", "mainAuthor", "coAuthor", "Publisher", "placeofPublication", "copyrightDate", "publicationDate", "Editors", "accessionNumber", "Location", "Language", "Type", "is_borrowed", "borrowed_by", "student_id", "borrow_date", "return_date"))
        return JsonResponse({"books": books_data})

    return render(request, "records.html", {
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
    total_accounts = Account.objects.count()
    total_borrows_all_time = BorrowHistory.objects.count()
    # count books marked as Borrowed in Book.status
    currently_borrowed = Book.objects.filter(status='Borrowed').count()
    available_books = Book.objects.filter(status='Available').count()
    
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
    period_new_accounts = Account.objects.filter(created_at__gte=start_date).count()
    
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
    location_stats = Book.objects.values('Location').annotate(
        total=Count('id'),
        borrowed=Count('id', filter=Q(status='Borrowed')),
        available=Count('id', filter=Q(status='Available'))
    ).order_by('-total')

    # ========== BATCH STATISTICS ==========
    batch_stats = Account.objects.values('batch').annotate(
        count=Count('id')
    ).order_by('batch')

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
    }

    context = {
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

        # Recent activity & overdue
        "borrowed_books": recent_activity,
        "overdue_list": overdue_list,

        # Chart data
        "metrics_json": json.dumps(metrics),
    }

    return render(request, "analytics.html", context)