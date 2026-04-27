"""
Views for accounts app.
"""
from urllib.parse import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.urls import get_script_prefix, reverse, reverse_lazy, set_script_prefix
from django.views.generic.edit import FormView
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from datetime import timedelta, datetime
from .models import User, EmailVerificationToken, CITICertificate


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
    """User profile view. Includes CITI status so researchers can see and manage certificates."""
    from .citi_utils import get_researcher_citi_status
    citi_status = get_researcher_citi_status(request.user)
    certs = list(CITICertificate.objects.filter(user=request.user).order_by('-expiration_date'))
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'profile': request.user.profile,
        'citi_status': citi_status,
        'citi_certificates': certs,
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


@login_required
def add_citi_certificate(request):
    """Let a researcher (or staff) add a CITI certificate to their profile."""
    if not (getattr(request.user, 'is_researcher', False) or getattr(request.user, 'is_staff', False)):
        return HttpResponseForbidden('Only researchers and staff can add CITI certificates.')

    if request.method == 'POST':
        completion_str = request.POST.get('completion_date', '').strip()
        expiration_str = request.POST.get('expiration_date', '').strip()
        if not completion_str or not expiration_str:
            messages.error(request, 'Completion date and expiration date are required.')
            return redirect('accounts:add_citi_certificate')

        try:
            completion = datetime.strptime(completion_str, '%Y-%m-%d').date()
            expiration = datetime.strptime(expiration_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Dates must be in YYYY-MM-DD format.')
            return redirect('accounts:add_citi_certificate')

        record_id = request.POST.get('record_id', '').strip()
        course_name = request.POST.get('course_name', '').strip()
        cert_file = request.FILES.get('certificate_file')

        cert = CITICertificate.objects.create(
            user=request.user,
            completion_date=completion,
            expiration_date=expiration,
            record_id=record_id,
            course_name=course_name,
        )
        if cert_file:
            cert.certificate_file = cert_file
            cert.save(update_fields=['certificate_file'])

        messages.success(request, f'CITI certificate added. Valid through {cert.expiration_date}.')
        return redirect('accounts:profile')

    return render(request, 'accounts/add_citi_certificate.html', {
        'user': request.user,
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


def _script_prefix_for_reset_email():
    """
    Return WSGI script prefix (with trailing slash) for {% url %} inside password-reset
    emails, or None to keep the current thread prefix.
    """
    fsn = (getattr(settings, 'FORCE_SCRIPT_NAME', None) or '').strip()
    if fsn:
        return fsn if fsn.endswith('/') else fsn + '/'
    site_url = (getattr(settings, 'SITE_URL', '') or '').strip()
    pl = urlparse(site_url)
    if pl.path and pl.path not in ('', '/'):
        p = pl.path
        return p if p.endswith('/') else p + '/'
    return None


def _password_reset_email_link_context(request):
    """Override domain/protocol/site_name in the reset email from SITE_URL (public site)."""
    site_url = (getattr(settings, 'SITE_URL', '') or '').strip()
    pl = urlparse(site_url)
    if not pl.hostname:
        return {}
    if pl.scheme in ('http', 'https'):
        protocol = pl.scheme
    else:
        protocol = 'https' if request.is_secure() else 'http'
    return {
        'domain': pl.hostname,
        'site_name': settings.SITE_NAME,
        'protocol': protocol,
    }


class ConfiguredPasswordResetView(auth_views.PasswordResetView):
    """
    Build password-reset emails with:
    - Host and protocol from SITE_URL (avoids bad links when the proxy Host differs).
    - Script prefix from FORCE_SCRIPT_NAME or the path on SITE_URL so /hsirb/ appears in links.
    """

    def form_valid(self, form):
        old_prefix = get_script_prefix()
        desired = _script_prefix_for_reset_email()
        try:
            if desired is not None:
                set_script_prefix(desired)
            pl = urlparse((getattr(settings, 'SITE_URL', '') or '').strip())
            use_https = self.request.is_secure()
            if pl.hostname and pl.scheme in ('http', 'https'):
                use_https = pl.scheme == 'https'
            base_extra = self.extra_email_context or {}
            extra = {**base_extra, **_password_reset_email_link_context(self.request)}
            opts = {
                'use_https': use_https,
                'token_generator': self.token_generator,
                'from_email': self.from_email,
                'email_template_name': self.email_template_name,
                'subject_template_name': self.subject_template_name,
                'request': self.request,
                'html_email_template_name': self.html_email_template_name,
                'extra_email_context': extra,
            }
            form.save(**opts)
        finally:
            set_script_prefix(old_prefix)
        return FormView.form_valid(self, form)


