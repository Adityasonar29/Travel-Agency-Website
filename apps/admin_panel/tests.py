from decimal import Decimal
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.admin_panel.forms import DestinationForm
from apps.booking.models import Booking, Review
from apps.core.models import ContactMessage, Destination, EmailLog, Tour
from apps.core.utils.mailer import email_html_to_text

User = get_user_model()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="VOYAGE Tests <no-reply@example.test>",
)
class AdminAccountLifecycleTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="site-admin",
            email="admin@example.com",
            password="AdminPass123!",
            is_staff=True,
        )
        self.customer = User.objects.create_user(
            username="traveller",
            email="traveller@example.com",
            password="UserPass123!",
            first_name="Taylor",
            last_name="Traveller",
        )
        self.client.force_login(self.admin)

    def test_deactivation_emails_user_and_prevents_login(self):
        mail.outbox.clear()
        response = self.client.post(
            reverse("admin_panel:toggle_user", args=[self.customer.pk])
        )

        self.assertRedirects(response, reverse("admin_panel:users"))
        self.customer.refresh_from_db()
        self.assertFalse(self.customer.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["traveller@example.com"])
        self.assertIn("deactivated", mail.outbox[0].subject.lower())

        self.client.logout()
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username_or_email": "traveller@example.com",
                "password": "UserPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This VOYAGE account is deactivated")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_admin_sidebar_logout_uses_confirmation_overlay(self):
        response = self.client.get(reverse("admin_panel:dashboard"))

        self.assertContains(response, "id=\"logout-confirmation\"")
        self.assertContains(response, "data-open-logout-confirmation")
        self.assertContains(response, "Stay signed in")
        self.assertContains(response, "Yes, log out")

    def test_activation_sends_account_reactivation_email(self):
        self.customer.is_active = False
        self.customer.save(update_fields=["is_active"])
        mail.outbox.clear()

        response = self.client.post(
            reverse("admin_panel:toggle_user", args=[self.customer.pk])
        )

        self.assertRedirects(response, reverse("admin_panel:users"))
        self.customer.refresh_from_db()
        self.assertTrue(self.customer.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["traveller@example.com"])
        self.assertIn("reactivated", mail.outbox[0].subject.lower())
        email_log = EmailLog.objects.get(event="account_activated")
        self.assertIn("Your VOYAGE account is active again.", email_log.body_html)

        response = self.client.get(
            reverse("admin_panel:communications"), {"tab": "sent"}
        )
        self.assertNotContains(response, "<iframe")
        self.assertContains(response, "An administrator has reactivated your VOYAGE account.")

        email_log.body_html = ""
        email_log.save(update_fields=["body_html"])
        legacy_response = self.client.get(
            reverse("admin_panel:communications"), {"tab": "sent"}
        )
        self.assertNotContains(legacy_response, "<iframe")
        self.assertContains(
            legacy_response, "An administrator has reactivated your VOYAGE account."
        )

    def test_deleting_user_anonymizes_but_preserves_payment_booking(self):
        tour = Tour.objects.create(
            name="Alpine escape",
            price_per_person=Decimal("350.00"),
        )
        booking = Booking.objects.create(
            user=self.customer,
            tour=tour,
            full_name="Taylor Traveller",
            email="traveller@example.com",
            phone="+123456789",
            special_requests="Please call me at my office.",
            payment_status="paid",
            payment_transaction_id="txn-retained",
            invoice_email="traveller@example.com",
            invoice_pdf_path="invoices/invoice_private.pdf",
        )
        payment_response = self.client.get(reverse("admin_panel:payments"))
        self.assertContains(payment_response, "$350.00")

        contact = ContactMessage.objects.create(
            name="Taylor Traveller",
            email="traveller@example.com",
            subject="A question",
            message="Please contact me.",
        )
        email_log = EmailLog.objects.create(
            recipient="traveller@example.com",
            subject="Booking update",
            body_text="A private message.",
        )

        response = self.client.post(
            reverse("admin_panel:delete_user", args=[self.customer.pk])
        )

        self.assertRedirects(response, reverse("admin_panel:users"))
        self.assertFalse(User.objects.filter(pk=self.customer.pk).exists())
        booking.refresh_from_db()
        self.assertIsNone(booking.user)
        self.assertEqual(booking.full_name, "Deleted account")
        self.assertEqual(booking.email, "")
        self.assertEqual(booking.phone, "")
        self.assertEqual(booking.special_requests, "")
        self.assertEqual(booking.total_amount, Decimal("350.00"))
        self.assertEqual(booking.payment_status, "paid")
        self.assertEqual(booking.payment_transaction_id, "txn-retained")
        self.assertEqual(booking.invoice_email, "")
        self.assertIsNone(booking.invoice_pdf_path)
        self.assertFalse(ContactMessage.objects.filter(pk=contact.pk).exists())
        self.assertFalse(EmailLog.objects.filter(pk=email_log.pk).exists())

    def test_destination_form_accepts_url_and_places_coordinates_after_featured(self):
        form = DestinationForm()

        self.assertEqual(
            list(form.fields).index("is_featured") + 1,
            list(form.fields).index("latitude"),
        )
        self.assertEqual(
            list(form.fields).index("latitude") + 1,
            list(form.fields).index("longitude"),
        )
        self.assertEqual(form.fields["image_url"].label, "Image URL")
        self.assertEqual(form.fields["hover_image_url"].label, "Hover image URL")

    def test_unsaved_tour_uses_its_fallback_rating(self):
        tour = Tour(
            name="Draft tour",
            price_per_person=Decimal("100.00"),
            rating=Decimal("4.2"),
        )

        self.assertEqual(tour.current_rating, Decimal("4.2"))

    def test_destination_list_uses_review_rating_and_links_to_coordinates(self):
        destination = Destination.objects.create(
            name="Cliffside",
            country="Testland",
            latitude=12.3456,
            longitude=-78.9012,
        )
        tour = Tour.objects.create(
            name="Cliffside tour",
            price_per_person=Decimal("300.00"),
        )
        tour.destinations.add(destination)
        booking = Booking.objects.create(
            user=self.customer,
            tour=tour,
            full_name="Taylor Traveller",
            email="traveller@example.com",
            phone="+123456789",
        )
        Review.objects.create(
            booking=booking,
            user=self.customer,
            rating=3,
            comment="A lovely trip.",
        )

        response = self.client.get(reverse("admin_panel:destinations"))

        self.assertEqual(destination.current_rating, 3.0)
        self.assertContains(response, "★ 3.0")
        self.assertContains(
            response,
            "https://www.google.com/maps/search/?api=1&amp;query=12.3456,-78.9012",
        )

    def test_contact_reply_uses_loading_form_and_records_sent_reply(self):
        contact = ContactMessage.objects.create(
            name="A Traveller",
            email="visitor@example.com",
            subject="Trip question",
            message="Can you help me plan a trip?",
        )
        mail.outbox.clear()

        response = self.client.get(reverse("admin_panel:communications"))
        self.assertContains(response, 'data-voyage-loading-form')
        self.assertContains(response, "Customer message")
        self.assertContains(response, "Your reply")
        self.assertNotContains(response, "<th>Event</th>")
        self.assertNotContains(response, "<th>Template</th>")

        response = self.client.post(
            reverse("admin_panel:reply_to_contact", args=[contact.pk]),
            {"subject": "Re: Trip question", "reply_body": "We can help."},
        )

        self.assertRedirects(
            response, f"{reverse('admin_panel:communications')}?tab=contacts"
        )
        contact.refresh_from_db()
        self.assertTrue(contact.is_replied)
        self.assertEqual(contact.reply_body, "We can help.")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["visitor@example.com"])
        email_log = EmailLog.objects.get(event="contact_reply")
        self.assertEqual(email_log.sender, "no-reply@example.test")
        self.assertEqual(email_log.recipient, "visitor@example.com")
        self.assertEqual(email_log.body_text, "We can help.")

    def test_compose_message_sends_and_logs_plain_message(self):
        mail.outbox.clear()

        response = self.client.post(
            reverse("admin_panel:compose_message"),
            {
                "recipient": "traveller@example.com",
                "subject": "Your custom itinerary",
                "body": "We have prepared your itinerary.",
            },
        )

        self.assertRedirects(
            response, f"{reverse('admin_panel:communications')}?tab=sent"
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["traveller@example.com"])
        email_log = EmailLog.objects.get(event="admin_composed")
        self.assertEqual(email_log.sender, "no-reply@example.test")
        self.assertEqual(email_log.body_text, "We have prepared your itinerary.")

    def test_email_text_extraction_omits_styles_and_preserves_message(self):
        text = email_html_to_text(
            "<html><head><style>body{color:red}</style></head>"
            "<body><p>First line</p><p>Second &amp; final line</p></body></html>"
        )

        self.assertEqual(text, "First line\n\nSecond & final line")

    def test_sent_tab_shows_distinct_sender_and_recipient_and_cleans_old_css(self):
        EmailLog.objects.create(
            sender="admin@example.com",
            recipient="customer@example.com",
            subject="A reply",
            body_text="body{color:red}table{border-collapse:legacy-css-test}.shell{width:100%}VOYAGE We have replied with your trip details.",
        )

        response = self.client.get(
            reverse("admin_panel:communications"), {"tab": "sent"}
        )

        self.assertContains(response, "admin@example.com")
        self.assertContains(response, "customer@example.com")
        display_body = response.context["email_logs"][0].display_body
        self.assertIn("We have replied with your trip details.", display_body)
        self.assertNotIn("body{color:red}", display_body)
        self.assertNotIn("border-collapse:legacy-css-test", display_body)

    def test_contact_acknowledgement_preview_uses_saved_customer_message(self):
        sent_at = timezone.now()
        ContactMessage.objects.create(
            name="A Traveller",
            email="customer@example.com",
            subject="Island trip",
            message="Please send details about the island trip.",
            is_replied=False,
        )
        EmailLog.objects.create(
            sender="admin@example.com",
            recipient="customer@example.com",
            subject="Island trip",
            event="contact_received_customer",
            body_text="body{color:red}table{border-collapse:legacy-css-test}",
            sent_at=sent_at,
        )

        response = self.client.get(
            reverse("admin_panel:communications"), {"tab": "sent"}
        )

        display_body = response.context["email_logs"][0].display_body
        self.assertIn("Please send details about the island trip.", display_body)
        self.assertNotIn("border-collapse:legacy-css-test", display_body)

    def test_admin_contact_notification_shows_only_original_enquiry_message(self):
        contact = ContactMessage.objects.create(
            name="A Traveller",
            email="customer@example.com",
            subject="Price drop",
            message="Do you also support the price drop offers?",
        )
        EmailLog.objects.create(
            sender="admin@example.com",
            recipient="hello@voyagetravel.com",
            subject="New contact message: Price drop",
            event="contact_received_admin",
            body_text=(
                "Price drop body{margin:0}table{border-collapse:collapse}"
                ".shell{width:100%}VOYAGETravel agency · thoughtfully arranged"
                "Message receivedThank you for reaching out."
            ),
            sent_at=contact.created_at,
        )

        response = self.client.get(
            reverse("admin_panel:communications"), {"tab": "sent"}
        )

        display_body = response.context["email_logs"][0].display_body
        self.assertEqual(display_body, "Do you also support the price drop offers?")

    def test_old_contact_reply_displays_the_saved_reply_not_template_markup(self):
        now = timezone.now()
        ContactMessage.objects.create(
            name="A Traveller",
            email="customer@example.com",
            subject="Trip",
            message="Please help.",
            is_replied=True,
            reply_subject="Re: Trip",
            reply_body="Here is the older reply.",
            replied_at=now - timedelta(hours=2),
        )
        ContactMessage.objects.create(
            name="A Traveller",
            email="customer@example.com",
            subject="Trip",
            message="Please help again.",
            is_replied=True,
            reply_subject="Re: Trip",
            reply_body="Here is the latest reply.",
            replied_at=now,
        )
        EmailLog.objects.create(
            sender="admin@example.com",
            recipient="customer@example.com",
            subject="Re: Trip",
            event="contact_reply",
            body_text="body{color:red}VOYAGE huge email layout CSS and boilerplate",
            sent_at=now - timedelta(hours=2),
        )
        EmailLog.objects.create(
            sender="admin@example.com",
            recipient="customer@example.com",
            subject="Re: Trip",
            event="contact_reply",
            body_text="body{color:red}VOYAGE huge email layout CSS and boilerplate",
            sent_at=now,
        )

        response = self.client.get(
            reverse("admin_panel:communications"), {"tab": "sent"}
        )

        self.assertContains(response, "Here is the older reply.")
        self.assertContains(response, "Here is the latest reply.")
        self.assertNotContains(response, "huge email layout CSS")
        self.assertEqual(response.content.count(b"Here is the older reply."), 2)
        self.assertEqual(response.content.count(b"Here is the latest reply."), 2)

    def test_all_communication_tabs_show_every_matching_record_and_remain_searchable(self):
        ContactMessage.objects.bulk_create([
            ContactMessage(
                name="Traveller",
                email="traveller@example.com",
                subject=f"Question {index}",
                message="Need trip details.",
                is_replied=True,
            )
            for index in range(35)
        ])
        ContactMessage.objects.bulk_create([
            ContactMessage(
                name="Waiting Traveller",
                email="waiting@example.com",
                subject=f"Waiting question {index}",
                message="Need a response.",
            )
            for index in range(7)
        ])
        EmailLog.objects.bulk_create([
            EmailLog(
                sender="admin@example.com",
                recipient=f"traveller{index}@example.com",
                subject=f"Sent message {index}",
                body_text="A sent message.",
            )
            for index in range(35)
        ])

        contact_response = self.client.get(
            reverse("admin_panel:communications"), {"tab": "contacts"}
        )
        inbox_response = self.client.get(
            reverse("admin_panel:communications"),
            {"tab": "inbox"},
        )
        sent_response = self.client.get(
            reverse("admin_panel:communications"), {"tab": "sent"}
        )
        search_result = self.client.get(
            reverse("admin_panel:communications"),
            {"tab": "contacts", "q": "Question 34"},
        )

        self.assertEqual(len(contact_response.context["contact_messages"]), 42)
        self.assertEqual(len(inbox_response.context["contact_messages"]), 7)
        self.assertEqual(len(sent_response.context["email_logs"]), 35)
        self.assertContains(contact_response, "Question 34")
        self.assertContains(search_result, "Question 34")
