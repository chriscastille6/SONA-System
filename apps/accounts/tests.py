from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import User


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"],
)
class PasswordResetFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="jbennett15@nicholls.edu",
            password="TempPassword123!",
            first_name="Jaycee",
            last_name="Bennett",
            role="researcher",
            is_active=True,
        )

    def test_password_reset_page_renders(self):
        response = self.client.get(reverse("accounts:password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset.html")

    def test_password_reset_post_redirects_and_sends_email(self):
        response = self.client.post(
            reverse("accounts:password_reset"),
            {"email": self.user.email},
            follow=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("accounts:password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Password reset", mail.outbox[0].subject)
        self.assertIn("/accounts/reset/", mail.outbox[0].body)

    def test_password_reset_post_sends_email_for_irb_member(self):
        irb = User.objects.create_user(
            email="irb.member@nicholls.edu",
            password="TempPassword123!",
            first_name="Pat",
            last_name="Committee",
            role="irb_member",
            is_active=True,
        )
        mail.outbox.clear()
        response = self.client.post(
            reverse("accounts:password_reset"),
            {"email": irb.email},
            follow=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/accounts/reset/", mail.outbox[0].body)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"],
)
class PasswordChangeFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="changer@nicholls.edu",
            password="OriginalPassword123!",
            first_name="Casey",
            last_name="Rivera",
            role="irb_member",
            is_active=True,
        )

    def test_password_change_redirects_when_anonymous(self):
        response = self.client.get(reverse("accounts:password_change"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.url.startswith(settings.LOGIN_URL)
            or settings.LOGIN_URL in response.url
        )

    def test_password_change_post_updates_password(self):
        self.client.login(email=self.user.email, password="OriginalPassword123!")
        response = self.client.post(
            reverse("accounts:password_change"),
            {
                "old_password": "OriginalPassword123!",
                "new_password1": "BrandNewPassword456!",
                "new_password2": "BrandNewPassword456!",
            },
            follow=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("accounts:password_change_done"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("BrandNewPassword456!"))

    def test_password_change_page_renders_when_logged_in(self):
        self.client.login(email=self.user.email, password="OriginalPassword123!")
        response = self.client.get(reverse("accounts:password_change"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_change.html")
