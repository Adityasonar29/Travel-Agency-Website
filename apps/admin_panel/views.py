from django.shortcuts import render

from apps.accounts.models import User
from apps.booking.models import Booking
from apps.core.models import Destination, Tour

from .decorators import admin_required


@admin_required
def dashboard(request):

    context = {

        "total_users": User.objects.count(),

        "total_bookings": Booking.objects.count(),

        "pending_bookings":
            Booking.objects.filter(status="pending").count(),

        "confirmed_bookings":
            Booking.objects.filter(status="confirmed").count(),

        "completed_bookings":
            Booking.objects.filter(status="completed").count(),

        "cancelled_bookings":
            Booking.objects.filter(status="cancelled").count(),

        "total_destinations":
            Destination.objects.count(),

        "total_tours":
            Tour.objects.count(),

        "recent_bookings":
            Booking.objects.select_related("tour").order_by("-created_at")[:8],

        "recent_users":
            User.objects.order_by("-date_joined")[:8],

    }

    return render(
        request,
        "admin_panel/dashboard.html",
        context,
    )