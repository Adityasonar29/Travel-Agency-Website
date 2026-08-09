from django.urls import path
from . import views


app_name = 'booking'


urlpatterns = [

    # ========================================================
    # BOOKING CREATION
    # ========================================================

    path(
        '',
        views.booking_page,
        name='booking'
    ),

    path(
        'tour/<int:tour_pk>/',
        views.booking_page,
        name='booking_with_tour'
    ),

    path(
        'claim-draft/',
        views.claim_draft_booking,
        name='claim_draft'
    ),


    # ========================================================
    # INITIAL BOOKING CONFIRMATION
    # ========================================================
    #
    # This is your EXISTING page:
    #
    # /booking/confirmation/BK41056FD4/
    #
    # It means:
    # "We received your booking request."
    #
    # It does NOT mean payment is completed.
    # ========================================================

    path(
        'confirmation/<str:booking_id>/',
        views.booking_confirmation,
        name='booking_confirmation'
    ),


    # ========================================================
    # BOOKING OVERVIEW
    # ========================================================
    #
    # User reaches this from:
    #
    # Profile
    #   ↓
    # Complete the process
    #   ↓
    # Booking overview
    #
    # Example:
    # /booking/BK41056FD4/overview/
    # ========================================================

    path(
        '<str:booking_id>/overview/',
        views.booking_overview,
        name='booking_overview'
    ),


    # ========================================================
    # PAYMENT
    # ========================================================
    #
    # Example:
    # /booking/BK41056FD4/payment/
    #
    # Shows:
    # - Booking total
    # - Card payment
    # - UPI payment
    # ========================================================

    path(
        '<str:booking_id>/payment/',
        views.payment_page,
        name='payment'
    ),


    # ========================================================
    # START PAYMENT
    # ========================================================
    #
    # POST endpoint from the payment form.
    #
    # It validates the dummy card/UPI information and moves:
    #
    # payment_status:
    # pending → processing
    #
    # It does NOT mark the booking as paid yet.
    # ========================================================

    path(
        '<str:booking_id>/payment/process/',
        views.payment_process,
        name='payment_process'
    ),


    # ========================================================
    # PAYMENT PROCESSING
    # ========================================================
    #
    # Shows the 10-second dummy payment countdown.
    #
    # Example:
    # /booking/BK41056FD4/payment/processing/
    # ========================================================

    path(
        '<str:booking_id>/payment/processing/',
        views.payment_processing,
        name='payment_processing'
    ),


    # ========================================================
    # COMPLETE PAYMENT
    # ========================================================
    #
    # POST endpoint called by JavaScript after the 10-second
    # countdown finishes.
    #
    # This is the important server-side transition:
    #
    # payment_status = paid
    # status = confirmed
    # transaction_id = generated
    # payment_date = generated
    #
    # Then invoice generation happens.
    # ========================================================

    path(
        '<str:booking_id>/payment/complete/',
        views.payment_complete,
        name='payment_complete'
    ),


    # ========================================================
    # FINAL BOOKING CONFIRMED PAGE
    # ========================================================
    #
    # Only accessible after:
    #
    # payment_status = paid
    # status = confirmed
    #
    # Example:
    # /booking/BK41056FD4/confirmed/
    # ========================================================

    path(
        '<str:booking_id>/confirmed/',
        views.booking_confirmed,
        name='booking_confirmed'
    ),


    # ========================================================
    # REVIEW
    # ========================================================
    #
    # These are for AFTER the journey has actually happened.
    #
    # Flow:
    #
    # completed booking
    #       ↓
    # review
    #       ↓
    # submit review
    # ========================================================

    path(
        'review/<str:booking_id>/',
        views.review_page,
        name='review_page'
    ),
    
    path(
        'review/<str:booking_id>/submit/',
        views.submit_review,
        name='submit_review'
    ),
]