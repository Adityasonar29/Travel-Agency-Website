import os
from calendar import month_abbr
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.models import User
from apps.booking.models import Booking, STATUS_CHOICES
from apps.core.models import ContactMessage, Destination, EmailLog, Tour
from apps.core.utils import mailer

from .decorators import admin_required
from .forms import DestinationForm, TourForm

User = get_user_model()


def _search(queryset, query, fields):
    if not query:
        return queryset
    lookup = Q()
    for field in fields:
        lookup |= Q(**{f"{field}__icontains": query})
    return queryset.filter(lookup)


@admin_required
def dashboard(request):

    today = date.today()
    paid_bookings = Booking.objects.filter(payment_status="paid")
    total_revenue = paid_bookings.aggregate(total=Sum("total_amount"))["total"] or Decimal("0")
    month_revenue = paid_bookings.filter(payment_date__year=today.year, payment_date__month=today.month).aggregate(total=Sum("total_amount"))["total"] or Decimal("0")
    year_revenue = paid_bookings.filter(payment_date__year=today.year).aggregate(total=Sum("total_amount"))["total"] or Decimal("0")
    pending_revenue = Booking.objects.filter(payment_status__in=["pending", "processing"]).aggregate(total=Sum("total_amount"))["total"] or Decimal("0")
    monthly_revenue = []
    for offset in range(5, -1, -1):
        month = today.month - offset
        year = today.year
        while month <= 0:
            month += 12
            year -= 1
        value = paid_bookings.filter(payment_date__year=year, payment_date__month=month).aggregate(total=Sum("total_amount"))["total"] or Decimal("0")
        monthly_revenue.append({"label": month_abbr[month], "year": year, "value": float(value)})
    chart_max = max((item["value"] for item in monthly_revenue), default=0)
    for item in monthly_revenue:
        item["height"] = round((item["value"] / chart_max) * 100, 2) if chart_max else 0

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

        "active_users": User.objects.filter(is_active=True).count(),
        "total_revenue": total_revenue,
        "month_revenue": month_revenue,
        "year_revenue": year_revenue,
        "pending_revenue": pending_revenue,
        "monthly_revenue": monthly_revenue,

    }

    return render(
        request,
        "admin_panel/dashboard.html",
        context,
    )


@admin_required
def bookings(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    payment_status = request.GET.get("payment_status", "").strip()
    sort = request.GET.get("sort", "-created_at").strip()
    booking_list = Booking.objects.select_related("tour", "user")
    booking_list = _search(booking_list, query, ["booking_id", "full_name", "email", "destination_name", "tour__name"])
    if status:
        booking_list = booking_list.filter(status=status)
    if payment_status:
        booking_list = booking_list.filter(payment_status=payment_status)
    sort_fields = {"created_at", "-created_at", "travel_date", "-travel_date", "full_name", "-full_name", "total_amount", "-total_amount", "status", "-status", "payment_status", "-payment_status"}
    if sort not in sort_fields:
        sort = "-created_at"
    booking_list = booking_list.order_by(sort)
    return render(request, "admin_panel/bookings.html", {
        "bookings": booking_list,
        "query": query,
        "selected_status": status,
        "selected_payment_status": payment_status,
        "selected_sort": sort,
        "status_choices": STATUS_CHOICES,
        "payment_status_choices": Booking._meta.get_field("payment_status").choices,
    })


@admin_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking.objects.select_related("tour", "user"), pk=pk)
    return render(request, "admin_panel/booking_detail.html", {"booking": booking})


@require_POST
@admin_required
def update_booking_status(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    new_status = request.POST.get("status")
    valid_statuses = {choice[0] for choice in STATUS_CHOICES}
    if new_status not in valid_statuses:
        messages.error(request, "That booking status is not valid.")
    else:
        booking.status = new_status
        booking.save(update_fields=["status", "updated_at"])
        status_label = dict(STATUS_CHOICES).get(booking.status, booking.status)
        messages.success(request, f"Booking {booking.booking_id} marked {status_label.lower()}.")
    return redirect(request.POST.get("next") or "admin_panel:bookings")


@admin_required
def users(request):
    query = request.GET.get("q", "").strip()
    user_list = _search(User.objects.all(), query, ["username", "first_name", "last_name", "email"])
    return render(request, "admin_panel/users.html", {"users": user_list, "query": query})


@require_POST
@admin_required
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.pk == request.user.pk or user.is_superuser:
        messages.error(request, "Your account and superuser accounts cannot be deleted here.")
    else:
        username = user.get_username()
        user.delete()
        messages.success(request, f"User {username} was deleted.")
    return redirect("admin_panel:users")


@require_POST
@admin_required
def toggle_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.pk == request.user.pk:
        messages.error(request, "You cannot deactivate your own account.")
    else:
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        messages.success(request, f"User {user.username} is now {'active' if user.is_active else 'inactive'}.")
    return redirect("admin_panel:users")


@admin_required
def tours(request):
    query = request.GET.get("q", "").strip()
    tour_list = _search(Tour.objects.prefetch_related("destinations"), query, ["name", "summary", "budget_range"])
    return render(request, "admin_panel/tours.html", {"tours": tour_list, "query": query})


@admin_required
def tour_form(request, pk=None):
    tour = get_object_or_404(Tour, pk=pk) if pk else None
    form = TourForm(request.POST or None, instance=tour)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Tour {'updated' if tour else 'created'} successfully.")
        return redirect("admin_panel:tours")
    return render(request, "admin_panel/tour_form.html", {"form": form, "tour": tour})


@require_POST
@admin_required
def delete_tour(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    name = tour.name
    tour.delete()
    messages.success(request, f"Tour {name} was deleted.")
    return redirect("admin_panel:tours")


@admin_required
def destinations(request):
    query = request.GET.get("q", "").strip()
    destination_list = _search(Destination.objects.all(), query, ["name", "country", "city", "state"])
    return render(request, "admin_panel/destinations.html", {"destinations": destination_list, "query": query})


@admin_required
def destination_form(request, pk=None):
    destination = get_object_or_404(Destination, pk=pk) if pk else None
    form = DestinationForm(request.POST or None, request.FILES or None, instance=destination)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Destination {'updated' if destination else 'created'} successfully.")
        return redirect("admin_panel:destinations")
    return render(request, "admin_panel/destination_form.html", {"form": form, "destination": destination})


@require_POST
@admin_required
def delete_destination(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    name = destination.name
    destination.delete()
    messages.success(request, f"Destination {name} was deleted.")
    return redirect("admin_panel:destinations")


@admin_required
def payments(request):
    payment_list = Booking.objects.exclude(payment_status="pending").select_related("tour").order_by("-updated_at")
    return render(request, "admin_panel/payments.html", {"payments": payment_list})


@admin_required
def invoices(request):
    invoice_list = Booking.objects.exclude(invoice_status="unprocessed").select_related("tour").order_by("-updated_at")
    for invoice in invoice_list:
        if invoice.invoice_pdf_path:
            invoice.file_url = f"{settings.MEDIA_URL}invoices/{os.path.basename(invoice.invoice_pdf_path)}"
    return render(request, "admin_panel/invoices.html", {"invoices": invoice_list, "media_url": settings.MEDIA_URL})


@admin_required
def communications(request):
    contact_messages = ContactMessage.objects.all()[:100]
    email_logs = EmailLog.objects.all()[:100]
    return render(
        request,
        "admin_panel/communications.html",
        {"contact_messages": contact_messages, "email_logs": email_logs},
    )


@require_POST
@admin_required
def reply_to_contact(request, pk):
    contact_message = get_object_or_404(ContactMessage, pk=pk)
    reply_body = request.POST.get("reply_body", "").strip()
    if not reply_body:
        messages.error(request, "Write a reply before sending it.")
        return redirect("admin_panel:communications")

    subject = request.POST.get("subject", "").strip() or f"Re: {contact_message.subject}"
    try:
        mailer.send_generic_notification(
            to_email=contact_message.email,
            subject=subject,
            template_path="emails/contact_reply.html",
            context={
                "recipient_name": contact_message.name,
                "original_subject": contact_message.subject,
                "reply_body": reply_body,
                "support_email": settings.DEFAULT_FROM_EMAIL,
                "_email_event": "contact_reply",
            },
        )
    except Exception as exc:
        messages.error(request, f"The reply could not be sent: {exc}")
    else:
        contact_message.is_replied = True
        contact_message.save(update_fields=["is_replied"])
        messages.success(request, f"Reply sent to {contact_message.email}.")
    return redirect("admin_panel:communications")
