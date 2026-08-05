from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.core.models import Destination
from apps.booking.models import Booking
from apps.accounts.models import WishlistItem

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

    def test_profile_dashboard_shows_bookings_and_wishlist_counts(self):
        Booking.objects.create(
            user=self.user,
            destination=self.destination,
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
        self.assertContains(response, 'My Bookings')
        self.assertContains(response, 'Saved favourites')
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
