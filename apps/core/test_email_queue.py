from datetime import timedelta
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.core.models import EmailLog, OutboundEmail
from apps.core.utils.email_queue import process_next_email
from apps.core.utils.mailer import send_admin_message


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class OutboundEmailQueueTests(TestCase):
    def setUp(self):
        mail.outbox.clear()

    def test_email_is_queued_before_worker_sends_it(self):
        send_admin_message(
            "traveller@example.com",
            "Your itinerary",
            "Your itinerary is ready.",
        )

        queued_email = OutboundEmail.objects.get()
        email_log = EmailLog.objects.get()
        self.assertEqual(queued_email.status, "queued")
        self.assertEqual(email_log.status, "pending")
        self.assertEqual(mail.outbox, [])

        self.assertTrue(process_next_email())

        queued_email.refresh_from_db()
        email_log.refresh_from_db()
        self.assertEqual(queued_email.status, "sent")
        self.assertEqual(email_log.status, "sent")
        self.assertEqual(mail.outbox[0].to, ["traveller@example.com"])
        self.assertEqual(mail.outbox[0].body, "Your itinerary is ready.")

    def test_failed_delivery_is_retried_after_backoff(self):
        send_admin_message(
            "traveller@example.com",
            "Your itinerary",
            "Your itinerary is ready.",
        )
        queued_email = OutboundEmail.objects.get()

        with self.assertLogs("apps.core.utils.email_queue", level="ERROR"):
            with patch(
                "apps.core.utils.email_queue.EmailMultiAlternatives.send",
                side_effect=OSError("SMTP unavailable"),
            ):
                self.assertTrue(process_next_email())

        queued_email.refresh_from_db()
        self.assertEqual(queued_email.status, "queued")
        self.assertEqual(queued_email.attempts, 1)
        self.assertIn("SMTP unavailable", queued_email.last_error)
        self.assertGreater(queued_email.available_at, timezone.now())
        self.assertFalse(process_next_email())
        self.assertEqual(mail.outbox, [])

        queued_email.available_at = timezone.now() - timedelta(seconds=1)
        queued_email.save(update_fields=["available_at"])
        self.assertTrue(process_next_email())

        queued_email.refresh_from_db()
        self.assertEqual(queued_email.status, "sent")
        self.assertEqual(queued_email.attempts, 2)
        self.assertEqual(len(mail.outbox), 1)
