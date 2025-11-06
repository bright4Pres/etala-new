from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.shortcuts import render
from .models import Book, Account
from django.views.decorators.csrf import csrf_protect
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