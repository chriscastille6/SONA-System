"""
Views for accounts app.
"""
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from datetime import timedelta
from .models import User, EmailVerificationToken


def register(request):
    """User registration view."""
    if request.method == 'POST':
        # TODO: Implement registration form processing
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        role = request.POST.get('role', 'participant')
        
        if email and first_name and last_name and password:
            try:
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role=role
                )
                
                # Create email verification token
                token = EmailVerificationToken.objects.create(
                    user=user,
                    expires_at=timezone.now() + timedelta(days=7)
                )
                
                # TODO: Send verification email
                
                messages.success(request, 'Registration successful! Please check your email to verify your account.')
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'accounts/register.html')


def verify_email(request, token):
    """Email verification view."""
    verification_token = get_object_or_404(EmailVerificationToken, token=token)
    
    if verification_token.is_valid:
        user = verification_token.user
        user.email_verified_at = timezone.now()
        user.save()
        
        verification_token.used_at = timezone.now()
        verification_token.save()
        
        messages.success(request, 'Email verified successfully! You can now log in.')
        return redirect('accounts:login')
    else:
        messages.error(request, 'This verification link is invalid or has expired.')
        return redirect('accounts:resend_verification')


@login_required
def resend_verification(request):
    """Resend verification email."""
    if request.user.email_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('home')
    
    if request.method == 'POST':
        # Create new verification token
        token = EmailVerificationToken.objects.create(
            user=request.user,
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        # TODO: Send verification email
        
        messages.success(request, 'Verification email sent! Please check your inbox.')
        return redirect('home')
    
    return render(request, 'accounts/resend_verification.html')


@login_required
def profile(request):
    """User profile view."""
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'profile': request.user.profile
    })


@login_required
def edit_profile(request):
    """Edit user profile."""
    if request.method == 'POST':
        # TODO: Implement profile editing
        profile = request.user.profile
        profile.phone = request.POST.get('phone', '')
        profile.department = request.POST.get('department', '')
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/edit_profile.html', {
        'user': request.user,
        'profile': request.user.profile
    })


class RoleAwareLoginView(LoginView):
    """
    Override the default login view so we can land users on the most relevant dashboard.
    IRB members go to their dashboard, researchers to the researcher dashboard, etc.
    """
    template_name = 'accounts/login.html'

    def get_success_url(self):
        """Respect ?next= when safe, otherwise route by role."""
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return next_url

        user = self.request.user
        if getattr(user, 'is_irb_member', False):
            return reverse_lazy('studies:irb_member_dashboard')
        if getattr(user, 'is_researcher', False):
            return reverse_lazy('studies:researcher_dashboard')
        if getattr(user, 'is_participant', False):
            return reverse_lazy('studies:list')
        return settings.LOGIN_REDIRECT_URL



