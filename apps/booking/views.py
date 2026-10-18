import os
import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from apps.core.models import Tour, Destination
from .forms import BookingForm
from .models import Booking, Review
from apps.core.utils import mailer, invoice as invoice_utils


# ============================================================
# HELPERS
# ============================================================

def _generate_booking_id():
    """
    Generate a booking reference such as:
    BK41056FD4
    """
    return "BK" + "".join(
        [
            c
            for c in str(uuid.uuid4())[:8].upper()
            if c.isalnum()
        ][:8]
    )


def _generate_transaction_id():
    """
    Generate a dummy payment transaction ID.
    Example:
    VOY-PAY-A91F32C8
    """
    return "VOY-PAY-" + "".join(
        [
            c
            for c in str(uuid.uuid4())[:8].upper()
            if c.isalnum()
        ][:8]
    )


def _can_send_mail():
    """
    Check whether email sending is configured.

    Console email backend is allowed during development.
    """
    email_backend = getattr(
        settings,
        'EMAIL_BACKEND',
        ''
    )

    if email_backend == 'django.core.mail.backends.console.EmailBackend':
        return True

    email_user = (
        os.environ.get('EMAIL_HOST_USER', '')
        or getattr(settings, 'EMAIL_HOST_USER', '')
    )

    email_pass = (
        os.environ.get('EMAIL_HOST_PASSWORD', '')
        or getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    )

    return bool(email_user and email_pass)


def _lock_booking_total(booking):
    """
    Freeze the booking price.

    For curated tours:
        price per person × travellers

    Personalized journeys without a tour currently have
    no fixed price, so their total remains 0 until a tour/quote
    exists.
    """

    if booking.total_amount is not None:
        return booking.total_amount

    if booking.tour:
        total = (
            booking.tour.price_per_person
            * (booking.num_travelers or 1)
        )
    else:
        total = Decimal('0.00')

    booking.total_amount = total

    return total




def _prepare_booking_for_user(booking, user):
    """
    Attach a booking to the authenticated user and fill
    missing identity information from the account.
    """

    booking.user = user

    if not booking.full_name:
        booking.full_name = (
            user.get_full_name()
            or user.username
        )

    if not booking.email:
        booking.email = user.email

    booking.status = 'pending'

    # Payment must start in pending state.
    booking.payment_status = 'pending'

    # Lock the price at booking creation time.
    _lock_booking_total(booking)

    return booking


def _get_user_booking(request, booking_id):
    """
    Fetch a booking belonging to the currently authenticated user.

    This is used by every private booking/payment/review page.
    """
    return get_object_or_404(
        Booking.objects.select_related('tour', 'user'),
        booking_id=booking_id,
        user=request.user
    )


def _update_completed_bookings(user):
    """
    Automatically mark paid and confirmed bookings as completed
    after the journey has finished.
    """

    today = timezone.localdate()

    bookings = Booking.objects.filter(
        user=user,
        status='confirmed',
        payment_status='paid',
    )

    for booking in bookings:

        # If a return date exists, the journey finishes then.
        # Otherwise use the travel date.
        completion_date = (
            booking.return_date
            or booking.travel_date
        )

        if completion_date and completion_date < today:
            booking.status = 'completed'

            booking.save(
                update_fields=[
                    'status',
                    'updated_at',
                ]
            )

# ============================================================
# BOOKING CREATION
# ============================================================

def booking_page(request, tour_pk=None):
    """
    Multi-step booking flow.

    Step 1: Pick tour + destination
    Step 2: Traveler details
    Step 3: Preferences
    Step 4: Review & submit

    IMPORTANT:
    Submitting this form creates a PENDING booking request.
    It does NOT confirm the booking.

    Payment happens later from the user's journey archive.
    """

    submission_key = request.POST.get('booking_submission_key') or str(uuid.uuid4())
    step = (
        request.POST.get('step')
        or request.GET.get('step', '1')
    )

    initial_tour = None

    # --------------------------------------------------------
    # Determine selected tour
    # --------------------------------------------------------

    if tour_pk:
        initial_tour = get_object_or_404(
            Tour,
            pk=tour_pk
        )

    elif request.GET.get('tour'):
        tour_id = request.GET.get('tour')

        try:
            initial_tour = Tour.objects.get(
                pk=tour_id
            )
        except Tour.DoesNotExist:
            initial_tour = None

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == 'POST':

        form = BookingForm(
            request.POST,
            initial_tour=initial_tour
        )

        if form.is_valid():

            previous_key = request.session.get('booking_submission_key')
            previous_booking_id = request.session.get('booking_submission_booking_id')
            if previous_key and previous_key == submission_key and previous_booking_id:
                return redirect(
                    reverse(
                        'booking:booking_confirmation',
                        args=[previous_booking_id]
                    )
                )

            booking = form.save(
                commit=False
            )

            request_type = (
                form.cleaned_data.get('request_type')
            )

            # ------------------------------------------------
            # Destination handling
            # ------------------------------------------------

            if request_type == 'personalized':

                if not booking.destination_name:
                    booking.destination_name = ''

            if (
                booking.tour
                and not booking.destination_name
            ):
                destination = (
                    booking.tour.destinations.first()
                )

                booking.destination_name = (
                    destination.name
                    if destination
                    else ''
                )

            # ------------------------------------------------
            # Authenticated user
            # ------------------------------------------------

            if request.user.is_authenticated:

                _prepare_booking_for_user(
                    booking,
                    request.user
                )

                booking.save()
                request.session['booking_submission_key'] = submission_key
                request.session['booking_submission_booking_id'] = booking.booking_id
                request.session.modified = True

                messages.success(
                    request,
                    (
                        "Your booking request has been received. "
                        "Complete the payment from your journey "
                        "archive to confirm it."
                    )
                )

                _send_booking_emails(
                    request,
                    booking
                )

                return redirect(
                    reverse(
                        'booking:booking_confirmation',
                        args=[booking.booking_id]
                    )
                )

            # ------------------------------------------------
            # Guest booking
            # ------------------------------------------------

            booking.status = 'pending'
            booking.payment_status = 'pending'

            _lock_booking_total(
                booking
            )

            booking.save()
            request.session['booking_submission_key'] = submission_key
            request.session['booking_submission_booking_id'] = booking.booking_id
            request.session.modified = True

            request.session[
                'draft_booking_id'
            ] = booking.pk

            messages.info(
                request,
                (
                    "Your booking has been saved. "
                    "Please log in or register to continue."
                )
            )

            return redirect(
                f"{settings.LOGIN_URL}?next="
                f"{reverse('booking:claim_draft')}"
            )

        # ----------------------------------------------------
        # Invalid form
        # ----------------------------------------------------

        if (
            not request.user.is_authenticated
            and 'draft_booking_id'
            in request.session
        ):
            del request.session[
                'draft_booking_id'
            ]

        messages.error(
            request,
            "Please correct the errors in the form."
        )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    else:

        initial_data = {}

        if request.user.is_authenticated:

            initial_data['full_name'] = (
                request.user.get_full_name()
                or request.user.username
            )

            initial_data['email'] = (
                request.user.email
            )

        form = BookingForm(
            initial=initial_data,
            initial_tour=initial_tour
        )

    return render(
        request,
        'pages/booking.html',
        {
            'form': form,
            'step': step,
            'tour_pk': tour_pk,
            'tour_durations': {
                str(tour.pk): (tour.duration_days or 0)
                for tour in Tour.objects.all()
            },
            'booking_submission_key': submission_key,
        }
    )


# ============================================================
# CLAIM GUEST DRAFT AFTER LOGIN
# ============================================================

@login_required(login_url='/accounts/login/')
def claim_draft_booking(request):
    """
    Called after a guest logs in.

    The booking created before authentication is attached
    to the authenticated account and remains pending.
    """

    draft_id = request.session.pop(
        'draft_booking_id',
        None
    )

    if not draft_id:
        return redirect(
            reverse('booking:booking')
        )

    booking = get_object_or_404(
        Booking,
        pk=draft_id
    )

    # Prevent accidentally claiming another user's booking.
    if (
        booking.user
        and booking.user != request.user
    ):
        messages.error(
            request,
            "This booking cannot be claimed."
        )

        return redirect(
            reverse('core:home')
        )

    _prepare_booking_for_user(
        booking,
        request.user
    )

    booking.save()

    _send_booking_emails(
        request,
        booking
    )

    messages.success(
        request,
        (
            f"Booking {booking.booking_id} "
            "has been saved to your journey archive."
        )
    )

    return redirect(
        reverse(
            'booking:booking_confirmation',
            args=[booking.booking_id]
        )
    )


# ============================================================
# EXISTING BOOKING RECEIVED / CONFIRMATION PAGE
# ============================================================

@login_required(login_url='/accounts/login/')
def booking_confirmation(request, booking_id):
    """
    Existing booking-received page.

    IMPORTANT:
    This page does NOT mean payment has succeeded.

    It represents:
        Booking request received
        Payment still pending
    """

    booking = get_object_or_404(
        Booking,
        booking_id=booking_id
    )

    if booking.user != request.user:
        messages.error(
            request,
            "You don't have permission to view this booking."
        )

        return redirect(
            'core:home'
        )

    return render(
        request,
        'pages/booking_confirmation.html',
        {
            'booking': booking
        }
    )


# ============================================================
# BOOKING OVERVIEW
# ============================================================

@login_required(login_url='/accounts/login/')
def booking_overview(request, booking_id):
    """
    Display all details collected during booking.

    Pending:
        Continue to payment

    Confirmed:
        View confirmed journey

    Completed:
        Review journey
    """

    booking = _get_user_booking(
        request,
        booking_id
    )

    # Make sure older bookings created before
    # the payment system still have a total.
    if booking.total_amount is None:

        _lock_booking_total(
            booking
        )

        booking.save(
            update_fields=[
                'total_amount',
                'updated_at',
            ]
        )

    review = None

    try:
        review = booking.review
    except Review.DoesNotExist:
        review = None

    return render(
        request,
        'pages/booking_overview.html',
        {
            'booking': booking,
            'review': review,
            'can_pay': (
                booking.status == 'pending'
                and booking.payment_status
                in ['pending', 'failed']
                and booking.total_amount
                and booking.total_amount > 0
            ),
        }
    )


# ============================================================
# PAYMENT PAGE
# ============================================================

@login_required(login_url='/accounts/login/')
def payment_page(request, booking_id):
    """
    Payment method selection and dummy payment form.

    Supported:
        Card
        UPI
    """

    booking = _get_user_booking(
        request,
        booking_id
    )

    # Already paid
    if booking.payment_status == 'paid':

        return redirect(
            reverse(
                'booking:booking_confirmed',
                args=[booking.booking_id]
            )
        )

    # Already confirmed for some other reason
    if booking.status == 'confirmed':

        return redirect(
            reverse(
                'booking:booking_confirmed',
                args=[booking.booking_id]
            )
        )

    # Cancelled booking cannot be paid
    if booking.status == 'cancelled':

        messages.error(
            request,
            "This booking has been cancelled."
        )

        return redirect(
            reverse(
                'booking:booking_overview',
                args=[booking.booking_id]
            )
        )

    # --------------------------------------------------------
    # Ensure total exists
    # --------------------------------------------------------

    if booking.total_amount is None:

        _lock_booking_total(
            booking
        )

        booking.save(
            update_fields=[
                'total_amount',
                'updated_at',
            ]
        )

    # --------------------------------------------------------
    # Personalized booking without a tour
    # --------------------------------------------------------

    if not booking.total_amount or booking.total_amount <= 0:

        messages.warning(
            request,
            (
                "This personalized journey does not have "
                "a final price yet. Payment will become "
                "available once your journey has been priced."
            )
        )

        return redirect(
            reverse(
                'booking:booking_overview',
                args=[booking.booking_id]
            )
        )

    return render(
        request,
        'pages/payment.html',
        {
            'booking': booking,
        }
    )


# ============================================================
# START PAYMENT / VALIDATE PAYMENT METHOD
# ============================================================

@login_required(login_url='/accounts/login/')
def payment_process(request, booking_id):
    """
    Validate the selected payment method and move the booking
    into the PROCESSING state.

    The actual dummy 10-second countdown happens on the
    payment_processing page.

    This endpoint does NOT immediately mark the booking paid.
    """

    if request.method != 'POST':

        return redirect(
            reverse(
                'booking:payment',
                args=[booking_id]
            )
        )

    booking = _get_user_booking(
        request,
        booking_id
    )

    # --------------------------------------------------------
    # Safety checks
    # --------------------------------------------------------

    if booking.status != 'pending':

        messages.info(
            request,
            "This booking is no longer awaiting payment."
        )

        return redirect(
            reverse(
                'booking:booking_overview',
                args=[booking.booking_id]
            )
        )

    if booking.payment_status == 'paid':

        return redirect(
            reverse(
                'booking:booking_confirmed',
                args=[booking.booking_id]
            )
        )

    # --------------------------------------------------------
    # Payment method
    # --------------------------------------------------------

    payment_method = (
        request.POST.get('payment_method')
        or ''
    ).strip().lower()

    allowed_methods = {
        'card',
        'upi',
    }

    if payment_method not in allowed_methods:

        messages.error(
            request,
            "Please select a valid payment method."
        )

        return redirect(
            reverse(
                'booking:payment',
                args=[booking.booking_id]
            )
        )

    # --------------------------------------------------------
    # Dummy card / UPI validation
    #
    # We DO NOT store card numbers, CVV, UPI passwords,
    # or any sensitive payment credentials.
    # --------------------------------------------------------

    if payment_method == 'card':

        card_name = (
            request.POST.get('card_name')
            or ''
        ).strip()

        card_number = (
            request.POST.get('card_number')
            or ''
        ).replace(' ', '').replace('-', '')

        expiry = (
            request.POST.get('expiry')
            or ''
        ).strip()

        cvv = (
            request.POST.get('cvv')
            or ''
        ).strip()

        if not card_name:
            messages.error(
                request,
                "Please enter the cardholder name."
            )

            return redirect(
                reverse(
                    'booking:payment',
                    args=[booking.booking_id]
                )
            )

        if not card_number:
            messages.error(
                request,
                "Please enter a card number."
            )

            return redirect(
                reverse(
                    'booking:payment',
                    args=[booking.booking_id]
                )
            )

        if not expiry:
            messages.error(
                request,
                "Please enter the card expiry date."
            )

            return redirect(
                reverse(
                    'booking:payment',
                    args=[booking.booking_id]
                )
            )

        if not cvv:
            messages.error(
                request,
                "Please enter the CVV."
            )

            return redirect(
                reverse(
                    'booking:payment',
                    args=[booking.booking_id]
                )
            )

    elif payment_method == 'upi':

        upi_id = (
            request.POST.get('upi_id')
            or ''
        ).strip()

        if not upi_id:
            messages.error(
                request,
                "Please enter your UPI ID."
            )

            return redirect(
                reverse(
                    'booking:payment',
                    args=[booking.booking_id]
                )
            )

    # --------------------------------------------------------
    # Mark payment as processing
    # --------------------------------------------------------

    booking.payment_method = payment_method
    booking.payment_status = 'processing'

    booking.save(
        update_fields=[
            'payment_method',
            'payment_status',
            'updated_at',
        ]
    )

    return redirect(
        reverse(
            'booking:payment_processing',
            args=[booking.booking_id]
        )
    )


# ============================================================
# PAYMENT PROCESSING PAGE
# ============================================================

@login_required(login_url='/accounts/login/')
def payment_processing(request, booking_id):
    """
    Displays the 10-second dummy payment processing screen.

    The frontend countdown eventually calls:
        payment_complete()

    """

    booking = _get_user_booking(
        request,
        booking_id
    )

    if booking.payment_status == 'paid':

        return redirect(
            reverse(
                'booking:booking_confirmed',
                args=[booking.booking_id]
            )
        )

    if booking.payment_status != 'processing':

        return redirect(
            reverse(
                'booking:payment',
                args=[booking.booking_id]
            )
        )

    return render(
        request,
        'pages/payment_processing.html',
        {
            'booking': booking,
        }
    )


# ============================================================
# COMPLETE DUMMY PAYMENT
# ============================================================

@login_required(login_url='/accounts/login/')
def payment_complete(request, booking_id):
    """
    Final server-side step of the dummy payment.

    Called after the 10-second frontend countdown.

    This is where the booking actually changes to:

        payment_status = paid
        status = confirmed

    and where the transaction ID/payment date are generated.
    """

    if request.method != 'POST':

        return JsonResponse(
            {
                'success': False,
                'message': 'Invalid request method.'
            },
            status=405
        )

    # --------------------------------------------------------
    # Lock the booking row during confirmation.
    # --------------------------------------------------------

    with transaction.atomic():

        booking = get_object_or_404(
            Booking.objects.select_for_update(),
            booking_id=booking_id,
            user=request.user
        )

        # ----------------------------------------------------
        # Already completed
        # ----------------------------------------------------

        if booking.payment_status == 'paid':

            return JsonResponse(
                {
                    'success': True,
                    'already_paid': True,
                    'redirect_url': reverse(
                        'booking:booking_confirmed',
                        args=[booking.booking_id]
                    ),
                }
            )

        # ----------------------------------------------------
        # Must be processing
        # ----------------------------------------------------

        if booking.payment_status != 'processing':

            return JsonResponse(
                {
                    'success': False,
                    'message': (
                        'This payment is not currently '
                        'being processed.'
                    ),
                },
                status=400
            )

        # ----------------------------------------------------
        # Must have a valid amount
        # ----------------------------------------------------

        if (
            booking.total_amount is None
            or booking.total_amount <= 0
        ):

            booking.payment_status = 'failed'

            booking.save(
                update_fields=[
                    'payment_status',
                    'updated_at',
                ]
            )

            return JsonResponse(
                {
                    'success': False,
                    'message': (
                        'This booking does not have '
                        'a valid payment amount.'
                    ),
                },
                status=400
            )

        # ----------------------------------------------------
        # CONFIRM PAYMENT
        # ----------------------------------------------------

        booking.payment_status = 'paid'
        booking.status = 'confirmed'
        booking.payment_date = timezone.now()

        booking.payment_transaction_id = (
            _generate_transaction_id()
        )

        # Invoice number is generated by Booking.save()
        # because status is now confirmed.
        booking.save()

    # --------------------------------------------------------
    # Generate invoice AFTER payment succeeds.
    # --------------------------------------------------------

    try:

        booking.generate_invoice()

    except Exception as exc:

        # Payment is still successful even if invoice
        # generation has a problem.
        print(
            f"[INVOICE] Failed for {booking.booking_id}: {exc}"
        )

    # --------------------------------------------------------
    # Send final invoice email if possible.
    # --------------------------------------------------------

    try:

        if booking.invoice_pdf_path:
            booking.send_invoice()

    except Exception as exc:

        print(
            f"[INVOICE EMAIL] Failed for "
            f"{booking.booking_id}: {exc}"
        )

    # --------------------------------------------------------
    # Send final booking confirmation notification.
    # --------------------------------------------------------

    try:

        _send_payment_success_email(
            request,
            booking
        )

    except Exception as exc:

        print(
            f"[PAYMENT EMAIL] Failed for "
            f"{booking.booking_id}: {exc}"
        )

    return JsonResponse(
        {
            'success': True,
            'redirect_url': reverse(
                'booking:booking_confirmed',
                args=[booking.booking_id]
            ),
        }
    )


# ============================================================
# FINAL BOOKING CONFIRMED PAGE
# ============================================================

@login_required(login_url='/accounts/login/')
def booking_confirmed(request, booking_id):
    """
    Final success page shown after the dummy payment succeeds.
    """

    booking = _get_user_booking(
        request,
        booking_id
    )

    if (
        booking.status != 'confirmed'
        or booking.payment_status != 'paid'
    ):

        return redirect(
            reverse(
                'booking:booking_overview',
                args=[booking.booking_id]
            )
        )

    invoice_url = None
    
    if booking.invoice_pdf_path:
        invoice_url = (
            f"{settings.MEDIA_URL}"
            f"{booking.invoice_pdf_path}"
        )

    return render(
        request,
        'pages/booking_confirmed.html',
        {
            'booking': booking,
            'invoice_url': invoice_url,
        }
    )


@login_required(login_url='/accounts/login/')
def cancel_booking(request, booking_id):
    """Cancel an unpaid or paid booking from the member's journey archive."""
    if request.method != 'POST':
        return redirect(reverse('accounts:profile') + '#journeys')

    booking = _get_user_booking(request, booking_id)

    if booking.status in {'cancelled', 'completed'}:
        messages.info(request, 'This journey can no longer be cancelled.')
        return redirect(reverse('accounts:profile') + '#journeys')

    with transaction.atomic():
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = (request.POST.get('reason') or '').strip()
        if booking.payment_status == 'paid':
            booking.payment_status = 'refunded'
            booking.refund_status = 'pending'
        else:
            booking.refund_status = 'not_applicable'
        booking.save(update_fields=[
            'status', 'payment_status', 'refund_status', 'cancelled_at',
            'cancellation_reason', 'updated_at',
        ])

    if _can_send_mail():
        try:
            mailer.send_generic_notification(
                to_email=booking.email,
                subject=f'Journey cancellation received — {booking.booking_id}',
                template_path='emails/booking_cancelled.html',
                context={
                    'customer_name': booking.full_name or 'Traveller',
                    'booking_id': booking.booking_id,
                    'tour_name': booking.tour.name if booking.tour else booking.destination_name,
                    'travel_date': booking.travel_date,
                    'amount': booking.total_amount or 0,
                    'refund_pending': booking.refund_status == 'pending',
                    'support_email': settings.DEFAULT_FROM_EMAIL,
                },
            )
            if booking.refund_status == 'pending':
                mailer.send_generic_notification(
                    to_email=booking.email,
                    subject=f'Refund initiated — {booking.booking_id}',
                    template_path='emails/refund_initiated.html',
                    context={
                        'customer_name': booking.full_name or 'Traveller',
                        'booking_id': booking.booking_id,
                        'amount': booking.total_amount or 0,
                        'support_email': settings.DEFAULT_FROM_EMAIL,
                    },
                )
        except Exception as exc:
            print(f'[CANCELLATION EMAIL] Failed: {exc}')
    else:
        print(f'[CANCELLATION] Would email {booking.email} for {booking.booking_id}')

    if booking.refund_status == 'pending':
        messages.success(request, 'Your journey was cancelled. Your refund has been initiated and should arrive within 24 hours. Contact support if it does not.')
    else:
        messages.success(request, 'Your journey was cancelled and removed from your active trips.')
    return redirect(reverse('accounts:profile') + '#journeys')


# ============================================================
# REVIEW PAGE
# ============================================================

@login_required(login_url='/accounts/login/')
def review_page(request, booking_id):
    """
    Review page.

    A review is only allowed when:
        booking.status == completed
        booking belongs to the current user
        no review already exists
    """

    booking = _get_user_booking(
        request,
        booking_id
    )

    # --------------------------------------------------------
    # Booking must be completed
    # --------------------------------------------------------

    if booking.status != 'completed':

        messages.info(
            request,
            (
                "You can write a review after "
                "your journey has been completed."
            )
        )

        return redirect(
            reverse(
                'booking:booking_overview',
                args=[booking.booking_id]
            )
        )

    # --------------------------------------------------------
    # Already reviewed
    # --------------------------------------------------------

    try:
        existing_review = booking.review

    except Review.DoesNotExist:
        existing_review = None

    if existing_review:

        messages.info(
            request,
            "You have already reviewed this journey."
        )

        return redirect(
            reverse(
                'booking:booking_overview',
                args=[booking.booking_id]
            )
        )

    return render(
        request,
        'pages/review.html',
        {
            'booking': booking,
        }
    )


# ============================================================
# SUBMIT REVIEW
# ============================================================

@login_required(login_url='/accounts/login/')
def submit_review(request, booking_id):
    """
    Create one review for a completed booking.

    Review validation is intentionally kept here for now so
    we don't need to introduce another form file during the
    first implementation step.
    """

    if request.method != 'POST':

        return redirect(
            reverse(
                'booking:review',
                args=[booking_id]
            )
        )

    booking = _get_user_booking(
        request,
        booking_id
    )

    # --------------------------------------------------------
    # Must be completed
    # --------------------------------------------------------

    if booking.status != 'completed':

        messages.error(
            request,
            (
                "Only completed journeys "
                "can be reviewed."
            )
        )

        return redirect(
            reverse(
                'booking:booking_overview',
                args=[booking.booking_id]
            )
        )

    # --------------------------------------------------------
    # Prevent duplicate review
    # --------------------------------------------------------

    if Review.objects.filter(
        booking=booking
    ).exists():

        messages.info(
            request,
            "You have already reviewed this journey."
        )

        return redirect(
            reverse(
                'booking:booking_overview',
                args=[booking.booking_id]
            )
        )

    # --------------------------------------------------------
    # Read submitted values
    # --------------------------------------------------------

    rating_raw = (
        request.POST.get('rating')
        or ''
    ).strip()

    comment = (
        request.POST.get('comment')
        or ''
    ).strip()

    # --------------------------------------------------------
    # Validate rating
    # --------------------------------------------------------

    try:

        rating = int(rating_raw)

    except (
        TypeError,
        ValueError
    ):

        rating = 0

    if rating < 1 or rating > 5:

        messages.error(
            request,
            "Please select a rating from 1 to 5 stars."
        )

        return redirect(
            reverse(
                'booking:review',
                args=[booking.booking_id]
            )
        )

    # --------------------------------------------------------
    # Validate comment
    # --------------------------------------------------------

    if not comment:

        messages.error(
            request,
            "Please tell us a little about your journey."
        )

        return redirect(
            reverse(
                'booking:review',
                args=[booking.booking_id]
            )
        )

    if len(comment) > 5000:

        messages.error(
            request,
            "Your review is too long."
        )

        return redirect(
            reverse(
                'booking:review',
                args=[booking.booking_id]
            )
        )

    # --------------------------------------------------------
    # Create review
    # --------------------------------------------------------

    Review.objects.create(
        booking=booking,
        user=request.user,
        rating=rating,
        comment=comment,
    )

    messages.success(
        request,
        "Thank you for sharing your journey with us."
    )

    return redirect(
        reverse(
            'booking:booking_overview',
            args=[booking.booking_id]
        )
    )



# ============================================================
# INITIAL BOOKING EMAIL
# ============================================================

def _send_booking_emails(request, booking):
    """
    Sends the initial booking-received email.

    IMPORTANT:
    This happens while the booking is still pending.

    We intentionally DO NOT generate the final invoice here.
    The invoice is generated only after successful payment.
    """

    if not _can_send_mail():

        print(
            f"[BOOKING] Would email: "
            f"{booking.email} "
            f"(booking {booking.booking_id})"
        )

        return

    total_price = (
        booking.total_amount
        if booking.total_amount is not None
        else Decimal('0.00')
    )

    guest_context = {
        'customer_name': (
            booking.full_name
            or 'Guest'
        ),

        'booking_id': booking.booking_id,

        'tour_name': (
            booking.tour.name
            if booking.tour
            else ''
        ),

        'destination': (
            booking.destination_name
            or ''
        ),

        'start_date': booking.travel_date,

        'num_travelers': (
            booking.num_travelers
        ),

        'per_person_price': (
            booking.tour.price_per_person
            if booking.tour
            else Decimal('0.00')
        ),

        'total_price': total_price,

        'status': 'Pending Confirmation',

        'support_email': settings.DEFAULT_FROM_EMAIL,

        'view_booking_url': request.build_absolute_uri(
            reverse(
                'booking:booking_confirmation',
                args=[booking.booking_id]
            )
        ),

        # No invoice yet.
        'attachments': None,
    }

    try:

        mailer.send_booking_confirmation(
            booking.email,
            guest_context
        )

    except Exception as exc:

        print(
            f"[BOOKING EMAIL] Failed: {exc}"
        )

    # --------------------------------------------------------
    # Admin notification
    # --------------------------------------------------------

    admin_email = getattr(
        settings,
        'SITE_OWNER_EMAIL',
        settings.DEFAULT_FROM_EMAIL
    )

    if admin_email:

        admin_context = {
            'customer_name': booking.full_name,

            'booking_id': booking.booking_id,

            'tour_name': (
                booking.tour.name
                if booking.tour
                else ''
            ),

            'status': booking.status,

            'amount': total_price,
        }

        try:

            mailer.send_admin_booking_notification(
                admin_email,
                admin_context
            )

        except Exception as exc:

            print(
                f"[ADMIN BOOKING EMAIL] Failed: {exc}"
            )


# ============================================================
# FINAL PAYMENT SUCCESS EMAIL
# ============================================================

def _send_payment_success_email(request, booking):
    """
    Send a final notification after successful payment.

    This is separate from the initial booking-received email.
    """

    if not _can_send_mail():

        print(
            f"[PAYMENT] Would send confirmation: "
            f"{booking.email} "
            f"(booking {booking.booking_id})"
        )

        return

    total_price = (
        booking.total_amount
        or Decimal('0.00')
    )

    context = {
        'customer_name': (
            booking.full_name
            or 'Guest'
        ),

        'booking_id': booking.booking_id,

        'tour_name': (
            booking.tour.name
            if booking.tour
            else ''
        ),

        'destination': (
            booking.destination_name
            or ''
        ),

        'start_date': booking.travel_date,

        'num_travelers': booking.num_travelers,

        'total_price': total_price,

        'payment_method': (
            booking.get_payment_method_display()
        ),

        'payment_status': (
            booking.get_payment_status_display()
        ),

        'transaction_id': (
            booking.payment_transaction_id
        ),

        'status': booking.status,

        'invoice_url': (
            request.build_absolute_uri(
                f"{settings.MEDIA_URL}{booking.invoice_pdf_path}"
            )
            if booking.invoice_pdf_path
            else None
        ),

        'support_email': settings.DEFAULT_FROM_EMAIL,

        'view_booking_url': request.build_absolute_uri(
            reverse(
                'booking:booking_confirmed',
                args=[booking.booking_id]
            )
        ),

        'attachments': (
            [booking.invoice_pdf_path]
            if booking.invoice_pdf_path
            else None
        ),
    }

    # We use the existing mailer if it supports a generic
    # notification. If your mailer has a dedicated
    # confirmation function, we can swap it later.

    try:

        mailer.send_generic_notification(
            to_email=booking.email,
            subject=(
                f'Journey Confirmed — '
                f'{booking.booking_id}'
            ),
            template_path='emails/booking_confirmed.html',
            context=context,
            attachments=(
                [booking.invoice_pdf_path]
                if booking.invoice_pdf_path
                else None
            )
        )

    except Exception as exc:

        print(
            f"[PAYMENT SUCCESS EMAIL] Failed: {exc}"
        )
