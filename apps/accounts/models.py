from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser

ROLE_CHOICES = [
    ('customer', 'Customer'),
    ('admin', 'Admin'),
]

class User(AbstractUser):   
    phone = models.CharField(max_length=30, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    country = models.CharField(max_length=80, blank=True)
    is_verified = models.BooleanField(default=False)
    notification_emails = models.BooleanField(default=True)
    notification_sms = models.BooleanField(default=False)

    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer'
    )
        
    def __str__(self):
        return self.get_full_name() or self.username


class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    destination = models.ForeignKey('core.Destination', null=True, blank=True, on_delete=models.CASCADE)
    tour = models.ForeignKey('core.Tour', null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'destination'], name='unique_user_destination', condition=Q(destination__isnull=False)),
            models.UniqueConstraint(fields=['user', 'tour'], name='unique_user_tour', condition=Q(tour__isnull=False)),
        ]

    def clean(self):
        if bool(self.destination) == bool(self.tour):
            raise ValidationError('A wishlist item must reference exactly one destination or tour.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.destination:
            return f"{self.user.username} wishlist: {self.destination.name}"
        if self.tour:
            return f"{self.user.username} wishlist: {self.tour.name}"
        return f"{self.user.username} wishlist item"
