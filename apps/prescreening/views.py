"""
Views for prescreening app.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PrescreenQuestion, PrescreenResponse


@login_required
def prescreen_form(request):
    """Prescreen questionnaire form."""
    if not request.user.is_participant:
        messages.error(request, 'Only participants can complete the prescreen.')
        return redirect('home')
    
    # Get active questions
    questions = PrescreenQuestion.objects.filter(is_active=True).order_by('order')
    
    # Get existing response if any
    try:
        response = request.user.prescreen_response
    except PrescreenResponse.DoesNotExist:
        response = None
    
    return render(request, 'prescreening/form.html', {
        'questions': questions,
        'response': response
    })


@login_required
def submit_prescreen(request):
    """Submit prescreen responses."""
    if not request.user.is_participant:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        # Collect answers
        answers = {}
        questions = PrescreenQuestion.objects.filter(is_active=True)
        
        for question in questions:
            answer = request.POST.get(f'question_{question.id}')
            if answer:
                answers[str(question.id)] = answer
        
        # Save or update response
        response, created = PrescreenResponse.objects.update_or_create(
            participant=request.user,
            defaults={'answers': answers}
        )
        
        action = 'completed' if created else 'updated'
        messages.success(request, f'Prescreen {action} successfully!')
        return redirect('home')
    
    return redirect('prescreening:form')




