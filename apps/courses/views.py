"""
Views for courses app.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment


def course_list(request):
    """List all active courses."""
    courses = Course.objects.filter(is_active=True).order_by('-term', 'code')
    return render(request, 'courses/list.html', {'courses': courses})


def course_detail(request, pk):
    """Course detail view."""
    course = get_object_or_404(Course, pk=pk)
    
    # If participant, check if enrolled
    enrollment = None
    if request.user.is_authenticated and request.user.is_participant:
        enrollment = Enrollment.objects.filter(
            course=course,
            participant=request.user
        ).first()
    
    return render(request, 'courses/detail.html', {
        'course': course,
        'enrollment': enrollment
    })


@login_required
def my_courses(request):
    """View participant's enrolled courses or instructor's courses."""
    if request.user.is_participant:
        enrollments = Enrollment.objects.filter(
            participant=request.user
        ).select_related('course').order_by('-course__term')
        
        return render(request, 'courses/my_courses_participant.html', {
            'enrollments': enrollments
        })
    
    elif request.user.is_instructor or request.user.is_admin:
        courses = Course.objects.filter(instructor=request.user).order_by('-term')
        
        return render(request, 'courses/my_courses_instructor.html', {
            'courses': courses
        })
    
    return render(request, 'courses/my_courses.html')




