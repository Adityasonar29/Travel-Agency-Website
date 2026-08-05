from django.test import TestCase
from django.urls import reverse
from .models import ContactMessage


class ContactFormTests(TestCase):
    def test_contact_form_submits_and_saves_message(self):
        response = self.client.post(
            reverse('core:contact'),
            {
                'name': 'Ava Patel',
                'email': 'ava@example.com',
                'subject': 'Luxury itinerary inquiry',
                'message': 'I would love to plan a premium beach escape.',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thanks for reaching out')
        self.assertTrue(ContactMessage.objects.filter(email='ava@example.com').exists())
