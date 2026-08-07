from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_id', 'full_name', 'destination_name', 'travel_date',
        'num_travelers', 'status', 'payment_status', 'invoice_status',
        'created_at'
    )
    list_filter = (
        'status', 'payment_status', 'invoice_status',
        'created_at', 'travel_date'
    )
    list_editable = ('status', 'payment_status', 'invoice_status')
    search_fields = ('full_name', 'email', 'destination_name', 'booking_id')
    readonly_fields = ('created_at', 'updated_at', 'booking_id')
    fieldsets = (
        ('Booking Details', {
            'fields': ('booking_id', 'status', 'full_name', 'email', 'phone')
        }),
        ('Tour & Travel', {
            'fields': ('tour', 'destination_name', 'travel_date', 'num_travelers')
        }),
        ('Preferences', {
            'fields': ('budget_range', 'travel_style', 'special_requests')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_status', 'payment_transaction_id', 'payment_date')
        }),
        ('Invoice', {
            'fields': ('invoice_status', 'invoice_number', 'invoice_pdf_path',
                      'invoice_generated_at', 'invoice_sent_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    actions = ['generate_invoice', 'send_invoice', 'mark_confirmed']

    @admin.action(description='Generate invoice for selected bookings')
    def generate_invoice(self, request, queryset):
        for booking in queryset:
            try:
                booking.generate_invoice()
                self.message_user(request, f"Invoice generated for {booking.booking_id}")
            except Exception as e:
                self.message_user(request, f"Failed to generate invoice for {booking.booking_id}: {str(e)}", level='ERROR')

    @admin.action(description='Send invoice for selected bookings')
    def send_invoice(self, request, queryset):
        for booking in queryset:
            if booking.invoice_status == 'generated':
                booking.send_invoice()
                self.message_user(request, f"Invoice sent for {booking.booking_id}")
            else:
                self.message_user(request, f"Invoice not yet generated for {booking.booking_id}", level='WARNING')

    @admin.action(description='Mark selected bookings as confirmed')
    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
