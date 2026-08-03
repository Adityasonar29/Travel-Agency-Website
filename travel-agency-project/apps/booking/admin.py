from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'destination_name', 'travel_date', 'num_travelers', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    list_editable = ('status',)
    search_fields = ('full_name', 'email', 'destination_name')
    readonly_fields = ('created_at', 'updated_at')
