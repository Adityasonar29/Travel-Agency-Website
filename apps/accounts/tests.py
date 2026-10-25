import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.core.models import Destination, OutboundEmail
from apps.core.utils.email_queue import process_next_email
from apps.booking.models import Booking
from apps.accounts.models import PasswordResetPin, WishlistItem

User = get_user_model()


class AuthFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='demo_user',
            email='demo@example.com',
            password='StrongPass123!',
        )
        self.destination = Destination.objects.create(
            name='Test Destination',
            country='Testland',
            image='https://example.com/test.jpg',
            hero_image='https://example.com/test-hero.jpg',
        )
        OutboundEmail.objects.all().delete()

    def test_register_redirects_to_login_with_success_message(self):
        response = self.client.post(
            reverse('accounts:register'),
            {
                'username': 'newuser',
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'phone': '1234567890',
                'password1': 'StrongPass123!',
                'password2': 'StrongPass123!',
                'agree': 'on',
            },
            follow=True,
        )

        self.assertRedirects(response, reverse('accounts:login'))
        self.assertContains(response, 'Account created. Please log in.')

    def test_login_with_valid_credentials_shows_confirmation(self):
        response = self.client.post(
            reverse('accounts:login'),
            {
                'username_or_email': 'demo_user',
                'password': 'StrongPass123!',
                'remember_me': '',
            },
            follow=True,
        )

        self.assertRedirects(response, reverse('core:home'))
        self.assertContains(response, 'You are now logged in.')

    def test_login_queues_alert_without_waiting_for_email_delivery(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username_or_email": "demo_user",
                "password": "StrongPass123!",
                "remember_me": "",
            },
        )

        self.assertRedirects(response, reverse("core:home"))
        self.assertIn("_auth_user_id", self.client.session)
        queued_email = OutboundEmail.objects.get(recipient="demo@example.com")
        self.assertEqual(queued_email.status, "queued")
        self.assertEqual(mail.outbox, [])

    def test_logout_confirmation_overlay_is_rendered_and_logout_requires_post(self):
        self.client.force_login(self.user)

        page_response = self.client.get(reverse("core:home"))
        self.assertContains(page_response, 'id="logout-confirmation"')
        self.assertContains(page_response, "Stay signed in")
        self.assertContains(page_response, "Yes, log out")

        get_response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(get_response.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)

        post_response = self.client.post(reverse("accounts:logout"), follow=True)
        self.assertRedirects(post_response, reverse("core:home"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertContains(post_response, "You have been logged out.")

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_pin_can_be_requested_by_username_and_resets_password(self):
        mail.outbox.clear()

        request_response = self.client.post(
            reverse("accounts:forgot_password"),
            {"username_or_email": "demo_user"},
            follow=True,
        )

        self.assertEqual(request_response.status_code, 200)
        self.assertContains(request_response, "6-digit PIN sent")
        self.assertTrue(process_next_email())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["demo@example.com"])
        pin = re.search(r"\b(\d{6})\b", mail.outbox[0].body).group(1)
        reset_record = PasswordResetPin.objects.get(user=self.user)
        self.assertNotEqual(reset_record.pin_hash, pin)

        reset_response = self.client.post(
            reverse("accounts:reset_password"),
            {
                "pin": pin,
                "new_password1": "A-New-Strong-Password-981!",
                "new_password2": "A-New-Strong-Password-981!",
            },
            follow=True,
        )

        self.assertRedirects(reset_response, reverse("accounts:login"))
        self.assertContains(reset_response, "Your password has been reset")
        self.assertFalse(PasswordResetPin.objects.filter(user=self.user).exists())
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("A-New-Strong-Password-981!"))

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_can_be_requested_by_email_and_pin_is_single_use(self):
        mail.outbox.clear()
        self.client.post(
            reverse("accounts:forgot_password"),
            {"username_or_email": "DEMO@example.com"},
        )
        self.assertTrue(process_next_email())
        pin = re.search(r"\b(\d{6})\b", mail.outbox[0].body).group(1)

        response = self.client.post(
            reverse("accounts:reset_password"),
            {
                "pin": pin,
                "new_password1": "Another-Strong-Password-753!",
                "new_password2": "Another-Strong-Password-753!",
            },
        )

        self.assertRedirects(response, reverse("accounts:login"))
        self.assertFalse(PasswordResetPin.objects.filter(user=self.user).exists())
        self.assertFalse(self.client.login(
            username="demo_user",
            password="StrongPass123!",
        ))
        self.assertTrue(self.client.login(
            username="demo_user",
            password="Another-Strong-Password-753!",
        ))

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_unknown_user_does_not_reveal_account_existence(self):
        response = self.client.post(
            reverse("accounts:forgot_password"),
            {"username_or_email": "no-such-user"},
            follow=True,
        )

        self.assertContains(
            response,
            "If an active account matches those details, a password reset PIN has been sent",
        )
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(PasswordResetPin.objects.exists())

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_pin_expires_and_locks_after_five_incorrect_attempts(self):
        self.client.post(
            reverse("accounts:forgot_password"),
            {"username_or_email": "demo_user"},
        )
        reset_record = PasswordResetPin.objects.get(user=self.user)
        reset_record.expires_at = timezone.now() - timedelta(seconds=1)
        reset_record.save(update_fields=["expires_at"])

        expired_response = self.client.post(
            reverse("accounts:reset_password"),
            {
                "pin": "123456",
                "new_password1": "A-New-Strong-Password-981!",
                "new_password2": "A-New-Strong-Password-981!",
            },
            follow=True,
        )
        self.assertContains(expired_response, "PIN has expired")
        self.assertFalse(PasswordResetPin.objects.filter(user=self.user).exists())

        self.client.post(
            reverse("accounts:forgot_password"),
            {"username_or_email": "demo_user"},
        )
        for _ in range(5):
            response = self.client.post(
                reverse("accounts:reset_password"),
                {
                    "pin": "000000",
                    "new_password1": "A-New-Strong-Password-981!",
                    "new_password2": "A-New-Strong-Password-981!",
                },
            )

        self.assertRedirects(response, reverse("accounts:forgot_password"))
        self.assertFalse(PasswordResetPin.objects.filter(user=self.user).exists())

    def test_profile_dashboard_shows_bookings_and_wishlist_counts(self):
        Booking.objects.create(
            user=self.user,
            destination_name=self.destination.name,
            full_name='Demo User',
            email='demo@example.com',
            phone='+10000000000',
            travel_date='2026-12-01',
            num_travelers=2,
            budget_range='mid',
            travel_style='relaxed',
            special_requests='No rush',
            status='confirmed',
        )
        WishlistItem.objects.create(user=self.user, destination=self.destination)

        self.client.login(username='demo_user', password='StrongPass123!')
        response = self.client.get(reverse('accounts:profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Booking #')
        self.assertContains(response, 'Wishlist')
        self.assertContains(response, '#1')
        self.assertContains(response, 'Test Destination')

    def test_toggle_wishlist_adds_and_removes_item(self):
        self.client.login(username='demo_user', password='StrongPass123!')
        response = self.client.get(reverse('accounts:toggle_wishlist') + f'?destination={self.destination.id}&next={reverse("accounts:profile")}', follow=True)
        self.assertContains(response, 'Added Test Destination to your wishlist.')
        self.assertTrue(WishlistItem.objects.filter(user=self.user, destination=self.destination).exists())

        response = self.client.get(reverse('accounts:toggle_wishlist') + f'?destination={self.destination.id}&next={reverse("accounts:profile")}', follow=True)
        self.assertContains(response, 'Removed Test Destination from your wishlist.')
        self.assertFalse(WishlistItem.objects.filter(user=self.user, destination=self.destination).exists())
