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
from .views import home, books, about, register_account, check_duplicate, records, analytics
from .views_otp import get_students_by_grade, verify_student_email, verify_otp, resend_otp

urlpatterns = [
    path('', home, name='home'),
    path('home/', home, name='home'),
    path('analytics/', analytics, name='analytics'),
    path('books/', books, name='books'),
    path('register-account/', register_account, name='register_account'),
    path('check-duplicate/', check_duplicate, name='check_duplicate'),
    path('records/', records, name='records'),
    path('about/', about,  name='about'),
    
    # OTP Registration Flow
    path('api/get-students/', get_students_by_grade, name='get_students_by_grade'),
    path('api/verify-email/', verify_student_email, name='verify_student_email'),
    path('api/verify-otp/', verify_otp, name='verify_otp'),
    path('api/resend-otp/', resend_otp, name='resend_otp'),
]



