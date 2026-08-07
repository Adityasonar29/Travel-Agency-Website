import uuid
from django.db import models
from django.utils import timezone


def _generate_booking_id():
    return "BK" + "".join([c for c in str(uuid.uuid4())[:8].upper() if c.isalnum()][:8])


STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('cancelled', 'Cancelled'),
    ('completed', 'Completed'),
]

PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
    ('refunded', 'Refunded'),
]

PAYMENT_METHOD_CHOICES = [
    ('credit_card', 'Credit Card'),
    ('paypal', 'PayPal'),
    ('bank_transfer', 'Bank Transfer'),
    ('cash', 'Cash'),
]

INVOICE_STATUS_CHOICES = [
    ('unprocessed', 'Unprocessed'),
    ('processing', 'Processing'),
    ('generated', 'Generated'),
    ('sent', 'Sent'),
    ('failed', 'Failed'),
]

class Booking(models.Model):

    booking_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    tour = models.ForeignKey('core.Tour', on_delete=models.SET_NULL, null=True, blank=True)
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

    # Payment related fields
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)

    # Invoice related fields
    invoice_status = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES, default='unprocessed')
    invoice_email = models.EmailField(blank=True, null=True)
    invoice_pdf_path = models.CharField(max_length=255, blank=True, null=True)
    invoice_generated_at = models.DateTimeField(blank=True, null=True)
    invoice_sent_at = models.DateTimeField(blank=True, null=True)
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} — Booking {self.booking_id or self.id} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = _generate_booking_id()
        # Auto-generate invoice number if not set
        if not self.invoice_number and self.status == 'confirmed':
            self.invoice_number = f"INV-{self.booking_id}"
        super().save(*args, **kwargs)

    def generate_invoice(self):
        from apps.core.utils import invoice as invoice_utils
        try:
            invoice_path = invoice_utils.generate_invoice_for_booking(self)
            self.invoice_pdf_path = invoice_path
            self.invoice_status = 'generated'
            self.invoice_generated_at = timezone.now()
            self.save()
            return invoice_path
        except Exception as e:
            self.invoice_status = 'failed'
            self.save()
            raise e

    def send_invoice(self):
        from apps.core.utils import mailer
        from django.conf import settings

        if not self.email:
            return False

        invoice_url = f"{settings.MEDIA_URL}{self.invoice_pdf_path}" if self.invoice_pdf_path else None

        context = {
            'customer_name': self.full_name,
            'booking_id': self.booking_id,
            'invoice_number': self.invoice_number,
            'invoice_url': invoice_url,
            'invoice_pdf_path': self.invoice_pdf_path,
            'total_amount': self.tour.price_per_person * self.num_travelers if self.tour else 0,
            'created_at': self.created_at,
            'payment_method': self.get_payment_method_display(),
            'payment_status': self.get_payment_status_display(),
            'status': self.status,
        }

        try:
            mailer.send_generic_notification(
                to_email=self.email,
                subject=f'Invoice #{self.invoice_number} - Booking Confirmation',
                template_path='emails/invoice.html',
                context=context,
                attachments=[self.invoice_pdf_path] if self.invoice_pdf_path else None
            )
            self.invoice_status = 'sent'
            self.invoice_sent_at = timezone.now()
            self.save()
            return True
        except Exception as e:
            self.invoice_status = 'failed'
            self.save()
            return False
