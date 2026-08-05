from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import BookingForm
from apps.core.utils import mailer
from apps.core.utils import invoice as invoice_utils
from django.conf import settings
import os



@login_required(login_url='/accounts/login/')
def booking_page(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            messages.success(request, 'Your booking request has been submitted! We will contact you shortly.')

            # Send booking confirmation email (non-blocking)
            try:
                # Generate invoice PDF and attach
                invoice_path = None
                try:
                    invoice_path = invoice_utils.generate_invoice_for_booking(booking)
                except Exception:
                    invoice_path = None

                invoice_filename = invoice_path and invoice_path.split(os.sep)[-1] or ''

                # Prepare invoice summary data for the email template
                per_person_price = invoice_utils._try_parse_amount(getattr(booking, 'budget_range', None), default=30000)
                default_items = [
                    {'desc': 'Travel Package (per person)', 'qty': booking.num_travelers or 1, 'unit': per_person_price},
                    {'desc': 'Hotel', 'qty': 1, 'unit': 9000},
                    {'desc': 'Transportation', 'qty': 1, 'unit': 5000},
                ]
                for it in default_items:
                    it['total'] = it['qty'] * it['unit']
                subtotal = sum(it['total'] for it in default_items)
                tax = int(subtotal * 0.05)
                discount = 0
                grand_total = subtotal + tax - discount
                amount_paid_val = 0
                remaining_balance = grand_total - amount_paid_val

                context = {
                    'customer_name': booking.full_name,
                    'booking_id': booking.id,
                    'destination': booking.destination_name or (booking.destination.name if booking.destination else ''),
                    'start_date': booking.travel_date,
                    'end_date': '',
                    'num_travelers': booking.num_travelers,
                    'amount_paid': booking.budget_range or '',
                    'balance': '',
                    'view_booking_url': request.build_absolute_uri('/'),
                    'invoice_url': request.build_absolute_uri(settings.MEDIA_URL + f'invoices/{invoice_filename}') if invoice_filename else '#',
                    'attachments': [invoice_path] if invoice_path else None,
                    'items': default_items,
                    'subtotal': f"{subtotal:,}",
                    'tax': f"{tax:,}",
                    'discount': f"{discount:,}",
                    'grand_total': f"{grand_total:,}",
                    'amount_paid': f"{amount_paid_val:,}",
                    'remaining_balance': f"{remaining_balance:,}",
                    'invoice_id': f"INV-{booking.id:06d}",
                    'subject': 'Your Voyage Booking Confirmation',
                }
                mailer.send_booking_confirmation(booking.email, context)
            except Exception:
                # Don't break the flow if email fails during dev
                pass

            return redirect('core:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm()

    return render(request, 'pages/booking.html', {'form': form})
