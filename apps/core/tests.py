from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from apps.booking.models import Booking, Review
from .models import ContactMessage, Destination, OutboundEmail, Stat, Tour
from .utils.email_queue import process_next_email
from .utils.mailer import email_html_to_message_text


class ContactFormTests(TestCase):
    def test_public_page_statistics_use_admin_managed_stat_records(self):
        Stat.objects.all().delete()
        managed_stats = [
            Stat.objects.create(
                value=value,
                suffix=suffix,
                label=label,
                metric=metric,
                order=index,
            )
            for index, (value, suffix, label, metric) in enumerate(
                [
                    (0, "", "Managed Tours", "tours"),
                    (0, "", "Managed Destinations", "destinations"),
                    (0, "", "Managed Travelers", "travelers"),
                    (97, "%", "Managed Satisfaction", "satisfaction"),
                    (18, "+", "Managed Years", "manual"),
                ]
            )
        ]
        Destination.objects.create(name="Managed stats destination", country="India")
        tour = Tour.objects.create(
            name="Managed stats test tour",
            price_per_person=100,
        )
        confirmed_booking = Booking.objects.create(
            tour=tour,
            full_name="Test Traveler",
            email="traveler@example.com",
            phone="1234567890",
            num_travelers=3,
            status="confirmed",
        )
        completed_booking = Booking.objects.create(
            tour=tour,
            full_name="Another Traveler",
            email="another@example.com",
            phone="1234567891",
            num_travelers=2,
            status="completed",
        )
        Booking.objects.create(
            tour=tour,
            full_name="Cancelled Traveler",
            email="cancelled@example.com",
            phone="1234567892",
            num_travelers=10,
            status="cancelled",
        )
        user = get_user_model().objects.create_user(
            username="reviewer",
            email="reviewer@example.com",
            password="test-password",
        )
        Review.objects.create(
            booking=completed_booking,
            user=user,
            rating=4,
            comment="A lovely trip.",
        )
        pages = (
            "core:home",
            "core:destinations",
            "core:tours",
            "core:about",
        )

        for page_name in pages:
            with self.subTest(page=page_name):
                response = self.client.get(reverse(page_name))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    list(response.context["site_stats"]),
                    managed_stats[1:4] + managed_stats[:1],
                )
                self.assertEqual(len(response.context["site_stats"]), 4)
                for stat, expected_value in zip(
                    response.context["site_stats"],
                    ("1", "5", "80%", "1"),
                ):
                    self.assertContains(response, stat.label)
                    self.assertContains(response, expected_value)
                self.assertNotContains(response, "Managed Years")

    def test_email_message_extraction_excludes_styles_header_and_footer(self):
        rendered_email = (
            "<html><head><style>body{color:red}</style></head><body>"
            '<table><tr><td class="masthead">VOYAGE branding</td></tr>'
            '<tr><td class="body"><p class="eyebrow">Account update</p>'
            "<h1>Your account was updated</h1><p>The important message.</p></td></tr>"
            '<tr><td class="footer">Footer details</td></tr></table></body></html>'
        )

        self.assertEqual(
            email_html_to_message_text(rendered_email),
            "Account update\n\nYour account was updated\n\nThe important message.",
        )

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_contact_form_submits_and_saves_message(self):
        mail.outbox.clear()
        OutboundEmail.objects.all().delete()
        submitted_message = "I would love to plan a premium beach escape."
        response = self.client.post(
            reverse('core:contact'),
            {
                'name': 'Ava Patel',
                'email': 'ava@example.com',
                'subject': 'Luxury itinerary inquiry',
                'message': submitted_message,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thanks for reaching out')
        self.assertTrue(ContactMessage.objects.filter(email='ava@example.com').exists())
        while process_next_email():
            pass
        customer_email = next(
            message for message in mail.outbox if message.to == ['ava@example.com']
        )
        self.assertIn("Luxury itinerary inquiry", customer_email.body)
        self.assertIn(submitted_message, customer_email.body)
        self.assertIn(submitted_message, customer_email.alternatives[0][0])
