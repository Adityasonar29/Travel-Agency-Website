import os
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from apps.core.models import Tour, Destination
from .forms import BookingForm
from .models import Booking
from apps.core.utils import mailer, invoice as invoice_utils


def _generate_booking_id():
    return "BK" + "".join([c for c in str(uuid.uuid4())[:8].upper() if c.isalnum()][:8])


def _can_send_mail():
    email_backend = getattr(settings, 'EMAIL_BACKEND', '')
    if email_backend == 'django.core.mail.backends.console.EmailBackend':
        return True

    email_user = os.environ.get('EMAIL_HOST_USER', '') or getattr(settings, 'EMAIL_HOST_USER', '')
    email_pass = os.environ.get('EMAIL_HOST_PASSWORD', '') or getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    return bool(email_user and email_pass)


def booking_page(request, tour_pk=None):
    """
    Multi-step booking flow.
    Step 1: Pick tour + destination
    Step 2: Traveler details (name, email, phone, date, travelers)
    Step 3: Preferences (budget, style, requests)
    Step 4: Review & confirm
    """
    step = request.POST.get('step') or request.GET.get('step', '1')
    initial_tour = None

    # Check URL parameter first, then GET parameter
    if tour_pk:
        tour = get_object_or_404(Tour, pk=tour_pk)
        initial_tour = tour
    elif request.GET.get('tour'):
        tour_id = request.GET.get('tour')
        try:
            tour = Tour.objects.get(pk=tour_id)
            initial_tour = tour
        except Tour.DoesNotExist:
            pass

    if request.method == 'POST':
        form = BookingForm(request.POST, initial_tour=initial_tour)
        if form.is_valid():
            booking = form.save(commit=False)
        
            request_type = form.cleaned_data.get('request_type')
        
            if request_type == 'personalized':
                if not booking.destination_name:
                    booking.destination_name = ''
        
            if booking.tour and not booking.destination_name:
                dests = booking.tour.destinations.first()
                booking.destination_name = dests.name if dests else ''
        
            if request.user.is_authenticated:
                booking.user = request.user

                if not booking.full_name:
                    booking.full_name = (
                        request.user.get_full_name()
                        or request.user.username
                    )

                if not booking.email:
                    booking.email = request.user.email

                booking.status = 'pending'
                booking.save()

                messages.success(
                    request,
                    f"Booking confirmed! Your booking ID is {booking.booking_id}"
                )

                _send_booking_emails(request, booking)

                return redirect(
                    reverse(
                        'booking:booking_confirmation',
                        args=[booking.booking_id]
                    )
                )

            booking.status = 'pending'
            booking.save()

            request.session['draft_booking_id'] = booking.pk

            messages.info(
                request,
                "Please log in or register to continue your booking."
            )

            return redirect(
                f"{settings.LOGIN_URL}?next="
                f"{reverse('booking:claim_draft')}"
            )


        if not request.user.is_authenticated and 'draft_booking_id' in request.session:
            del request.session['draft_booking_id']
        messages.error(request, 'Please correct the errors in the form.')
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['full_name'] = request.user.get_full_name() or request.user.username
            initial_data['email'] = request.user.email
        form = BookingForm(initial=initial_data, initial_tour=initial_tour)

    return render(request, 'pages/booking.html', {
        'form': form,
        'step': step,
        'tour_pk': tour_pk,
    })


@login_required(login_url='/accounts/login/')
def claim_draft_booking(request):
    """
    Called right after login — picks up a draft the guest saved and confirms it.
    """
    draft_id = request.session.pop('draft_booking_id', None)
    if not draft_id:
        return redirect(reverse('booking:booking_page'))

    booking = get_object_or_404(Booking, pk=draft_id)
    booking.user = request.user
    booking.status = 'pending'
    if not booking.full_name:
        booking.full_name = request.user.get_full_name() or request.user.username
    if not booking.email:
        booking.email = request.user.email
    booking.save()

    _send_booking_emails(request, booking)
    messages.success(request, f"Welcome back! Booking {booking.booking_id} has been claimed and is now pending confirmation.")
    return redirect(reverse('booking:booking_confirmation', args=[booking.booking_id]))


def booking_confirmation(request, booking_id):
    """
    Show booking confirmation page.
    """
    booking = get_object_or_404(Booking, booking_id=booking_id)
    # Optional: Check if user owns this booking
    if booking.user and booking.user != request.user:
        messages.error(request, "You don't have permission to view this booking.")
        return redirect('core:home')

    return render(request, 'pages/booking_confirmation.html', {'booking': booking})


def _send_booking_emails(request, booking):
    """
    Sends confirmation email to the guest and a notification email to the site owner.
    Emails are only actually sent when not in DEBUG mode and credentials are present.
    """
    if not _can_send_mail():
        # dev — just log intent
        print(f"[BOOKING] Would email: {booking.email} (booking {booking.booking_id})")
        return

    invoice_path = None
    try:
        invoice_path = invoice_utils.generate_invoice_for_booking(booking)
    except Exception:
        invoice_path = None

    # Prepare a basic price estimate (per-person price from tour if available)
    per_person_price = 0
    if booking.tour:
        per_person_price = booking.tour.price_per_person

    guest_context = {
        'customer_name': booking.full_name or 'Guest',
        'booking_id': booking.booking_id,
        'tour_name': booking.tour.name if booking.tour else '',
        'destination': booking.destination_name or '',
        'start_date': booking.travel_date,
        'num_travelers': booking.num_travelers,
        'per_person_price': per_person_price,
        'total_price': per_person_price * (booking.num_travelers or 1),
        'status': 'Pending Confirmation',
        'view_booking_url': request.build_absolute_uri(
            reverse('booking:booking_confirmation', args=[booking.booking_id])
        ),
        'attachments': [invoice_path] if invoice_path else None,
    }

    mailer.send_booking_confirmation(booking.email, guest_context)

    # Admin notification
    admin_email = getattr(settings, 'SITE_OWNER_EMAIL', settings.DEFAULT_FROM_EMAIL)
    if admin_email:
        admin_context = {
            'customer_name': booking.full_name,
            'booking_id': booking.booking_id,
            'tour_name': booking.tour.name if booking.tour else '',
            'status': booking.status,
            'amount': per_person_price * (booking.num_travelers or 1),
        }
        mailer.send_admin_booking_notification(admin_email, admin_context)
