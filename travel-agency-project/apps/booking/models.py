from django.db import models


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    destination = models.ForeignKey('core.Destination', on_delete=models.CASCADE, null=True, blank=True)
    destination_name = models.CharField(max_length=200, blank=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    travel_date = models.DateField(blank=True, null=True)
    num_travelers = models.IntegerField(default=1)
    budget_range = models.CharField(max_length=50, blank=True)
    travel_style = models.CharField(max_length=100, blank=True)
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} — {self.destination_name} ({self.status})"
