"""
Views for credits app.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CreditTransaction


@login_required
def my_credits(request):
    """View participant's credit history."""
    if not request.user.is_participant:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    transactions = CreditTransaction.objects.filter(
        participant=request.user
    ).select_related('study', 'course', 'created_by').order_by('-created_at')
    
    # Calculate total credits
    total_credits = sum(t.amount for t in transactions)
    
    return render(request, 'credits/my_credits.html', {
        'transactions': transactions,
        'total_credits': total_credits
    })


@login_required
def grant_credits(request):
    """Grant credits (researcher/admin)."""
    if not (request.user.is_researcher or request.user.is_admin):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        # TODO: Implement credit granting form
        messages.success(request, 'Credits granted successfully!')
        return redirect('studies:researcher_dashboard')
    
    return render(request, 'credits/grant.html')




