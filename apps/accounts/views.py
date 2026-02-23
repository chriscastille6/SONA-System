"""
Views for accounts app.
"""
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from datetime import timedelta
from .models import User, EmailVerificationToken


def _send_verification_email(request, user, token):
    """Send email with verification link. Returns True if sent, False if email not configured."""
    if not getattr(settings, 'EMAIL_HOST', ''):
        return False
    verify_url = request.build_absolute_uri(
        reverse('accounts:verify_email', kwargs={'token': token.token})
    )
    subject = 'Verify your email - ' + getattr(settings, 'SITE_NAME', 'PRAMS')
    message = (
        f'Hi {user.get_full_name()},\n\n'
        f'Please verify your email by clicking the link below:\n\n'
        f'{verify_url}\n\n'
        f'This link expires in 7 days. If you did not create an account, you can ignore this email.\n'
    )
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=[user.email],
            fail_silently=True,
        )
        return True
    except Exception:
        return False


def register(request):
    """User registration view."""
    if request.method == 'POST':
        # TODO: Implement registration form processing
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        role = 'participant'  # Self-registration is participant only; other roles via admin/invite only.
        
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
                
                if _send_verification_email(request, user, token):
                    messages.success(request, 'Registration successful! Please check your email to verify your account.')
                else:
                    messages.warning(
                        request,
                        'Registration successful! Verification email could not be sent (email not configured). '
                        'You can request a new verification link from your profile after logging in.'
                    )
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
        
        if _send_verification_email(request, request.user, token):
            messages.success(request, 'Verification email sent! Please check your inbox and click the link.')
        else:
            messages.warning(
                request,
                'Verification email could not be sent (outgoing email is not configured on this server). '
                'Please contact an administrator to verify your email.'
            )
        return redirect('accounts:profile')
    
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



