from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        'booking_id',
        'full_name',
        'destination_name',
        'travel_date',
        'return_date',
        'num_travelers',
        'status',
        'payment_status',
        'invoice_status',
        'created_at',
    )

    list_filter = (
        'status',
        'payment_status',
        'invoice_status',
        'trip_purpose',
        'travel_style',
        'accommodation',
        'flexible_dates',
        'created_at',
        'travel_date',
    )

    list_editable = (
        'status',
        'payment_status',
        'invoice_status',
    )

    search_fields = (
        'full_name',
        'email',
        'phone',
        'destination_name',
        'booking_id',
        'origin',
        'additional_notes',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
        'booking_id',
    )

    fieldsets = (

        # =========================
        # BOOKING DETAILS
        # =========================
        ('Booking Details', {
            'fields': (
                'booking_id',
                'status',
                'user',
                'full_name',
                'email',
                'phone',
                'contact_preference',
            )
        }),

        # =========================
        # TOUR & DESTINATION
        # =========================
        ('Tour & Destination', {
            'fields': (
                'tour',
                'destination_name',
                'origin',
            )
        }),

        # =========================
        # TRAVEL DATES & PARTY
        # =========================
        ('Travel Dates & Travelers', {
            'fields': (
                'travel_date',
                'return_date',
                'flexible_dates',
                'num_travelers',
                'adults',
                'children',
            )
        }),

        # =========================
        # JOURNEY PREFERENCES
        # =========================
        ('Journey Preferences', {
            'fields': (
                'trip_purpose',
                'travel_style',
                'budget_range',
                'accommodation',
            )
        }),

        # =========================
        # PERSONALIZED REQUEST
        # =========================
        ('Personalized Journey', {
            'fields': (
                'transport_preferences',
                'experience_preferences',
                'dietary_requirements',
                'accessibility_requirements',
                'special_requests',
                'additional_notes',
            )
        }),

        # =========================
        # PAYMENT
        # =========================
        ('Payment', {
            'fields': (
                'payment_method',
                'payment_status',
                'payment_transaction_id',
                'payment_date',
                'total_amount',
            )
        }),

        # =========================
        # INVOICE
        # =========================
        ('Invoice', {
            'fields': (
                'invoice_status',
                'invoice_number',
                'invoice_pdf_path',
                'invoice_generated_at',
                'invoice_sent_at',
            )
        }),

        # =========================
        # TIMESTAMPS
        # =========================
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )

    actions = [
        'generate_invoice',
        'send_invoice',
        'mark_confirmed',
    ]

    @admin.action(description='Generate invoice for selected bookings')
    def generate_invoice(self, request, queryset):

        for booking in queryset:

            try:
                booking.generate_invoice()

                self.message_user(
                    request,
                    f"Invoice generated for {booking.booking_id}"
                )

            except Exception as e:

                self.message_user(
                    request,
                    f"Failed to generate invoice for "
                    f"{booking.booking_id}: {str(e)}",
                    level='ERROR'
                )

    @admin.action(description='Send invoice for selected bookings')
    def send_invoice(self, request, queryset):

        for booking in queryset:

            if booking.invoice_status == 'generated':

                booking.send_invoice()

                self.message_user(
                    request,
                    f"Invoice sent for {booking.booking_id}"
                )

            else:

                self.message_user(
                    request,
                    f"Invoice not yet generated for "
                    f"{booking.booking_id}",
                    level='WARNING'
                )

    @admin.action(description='Mark selected bookings as confirmed')
    def mark_confirmed(self, request, queryset):

        queryset.update(status='confirmed')