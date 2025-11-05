"""
URL configuration for lims_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import home, books, about, save_student, create_account, register_account, check_duplicate, records

urlpatterns = [
    path('', home, name='home'),
    path('home/', home, name='home'),
    path('books/', books, name='books'),
    path('create-account/', create_account, name='create_account'),
    path('save/', save_student, name='save_student'),
    path('register-account/', register_account, name='register_account'),
    path('check-duplicate/', check_duplicate, name='check_duplicate'),
    path('records/', records, name='records'),
    path('about/', about,  name='about')
]



