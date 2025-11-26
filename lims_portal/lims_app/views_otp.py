from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .models import StudentActivation, grade_Seven, grade_Eight, grade_Nine, grade_Ten, grade_Eleven, grade_Twelve
from .tasks import send_otp_email_task

# Grade models mapping
GRADE_MODELS = {
    7: grade_Seven,
    8: grade_Eight,
    9: grade_Nine,
    10: grade_Ten,
    11: grade_Eleven,
    12: grade_Twelve,
}


@require_http_methods(["POST"])
def get_students_by_grade(request):
    """Get all students for a specific grade."""
    try:
        data = json.loads(request.body)
        grade = int(data.get('grade'))
        
        if grade not in GRADE_MODELS:
            return JsonResponse({'error': 'Invalid grade'}, status=400)
        
        # Get all students from the selected grade
        grade_model = GRADE_MODELS[grade]
        students = grade_model.objects.all().values('id', 'name', 'school_id', 'email')
        
        return JsonResponse({
            'success': True,
            'students': list(students)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
def verify_student_email(request):
    """Verify that selected student's email matches the one entered."""
    try:
        data = json.loads(request.body)
        grade = int(data.get('grade'))
        student_id = int(data.get('student_id'))
        email = data.get('email', '').strip()
        
        if grade not in GRADE_MODELS:
            return JsonResponse({'error': 'Invalid grade'}, status=400)
        
        # Get student from the specific grade
        grade_model = GRADE_MODELS[grade]
        student = grade_model.objects.get(id=student_id)
        
        # Verify email matches
        if student.email.lower() != email.lower():
            return JsonResponse({
                'success': False,
                'error': 'Email does not match the student record'
            })
        
        # Email matches - now generate and send OTP
        activation, created = StudentActivation.objects.get_or_create(
            school_id=student.school_id,
            defaults={
                'name': student.name,
                'email': student.email,
                'grade': grade,
            }
        )
        
        # Generate OTP
        otp = activation.generate_otp()
        
        # Send OTP via Celery task (async)
        send_otp_email_task.delay(activation.email, otp, activation.name)
        
        return JsonResponse({
            'success': True,
            'message': f'OTP sent to {student.email}',
            'activation_id': activation.id,  # We'll need this for verification
        })
    except grade_model.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
def verify_otp(request):
    """Verify OTP entered by student."""
    try:
        data = json.loads(request.body)
        activation_id = int(data.get('activation_id'))
        otp = data.get('otp', '').strip()
        
        if not otp or len(otp) != 6:
            return JsonResponse({
                'success': False,
                'error': 'OTP must be 6 digits'
            })
        
        activation = StudentActivation.objects.get(id=activation_id)
        
        # Check if OTP is expired
        if activation.is_otp_expired():
            return JsonResponse({
                'success': False,
                'error': 'OTP has expired. Please request a new one.'
            })
        
        # Verify OTP
        if activation.verify_otp(otp):
            return JsonResponse({
                'success': True,
                'message': 'Account activated successfully!',
                'student_name': activation.name,
                'school_id': activation.school_id,
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid OTP. Please try again.'
            })
    except StudentActivation.DoesNotExist:
        return JsonResponse({'error': 'Activation record not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
def resend_otp(request):
    """Resend OTP to student."""
    try:
        data = json.loads(request.body)
        activation_id = int(data.get('activation_id'))
        
        activation = StudentActivation.objects.get(id=activation_id)
        
        # Generate new OTP
        otp = activation.generate_otp()
        
        # Send OTP via Celery task
        send_otp_email_task.delay(activation.email, otp, activation.name)
        
        return JsonResponse({
            'success': True,
            'message': f'OTP resent to {activation.email}'
        })
    except StudentActivation.DoesNotExist:
        return JsonResponse({'error': 'Activation record not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
