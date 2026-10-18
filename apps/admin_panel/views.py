import os
from calendar import month_abbr
from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
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
        email = user.email
        profile_image = user.profile_image
        booking_ids = list(
            user.bookings.exclude(booking_id__isnull=True)
            .values_list("booking_id", flat=True)
        )
        invoice_paths = list(
            user.bookings.exclude(invoice_pdf_path__isnull=True)
            .exclude(invoice_pdf_path="")
            .values_list("invoice_pdf_path", flat=True)
        )
        with transaction.atomic():
            user.bookings.update(
                user=None,
                full_name="Deleted account",
                email="",
                phone="",
                budget_range="",
                travel_style="",
                special_requests="",
                origin="",
                flexible_dates=False,
                trip_purpose="",
                accommodation="",
                transport_preferences="",
                experience_preferences="",
                dietary_requirements="",
                accessibility_requirements="",
                additional_notes="",
                contact_preference="email",
                cancellation_reason="",
                invoice_email="",
                invoice_pdf_path=None,
            )
            if email:
                ContactMessage.objects.filter(email__iexact=email).delete()
                EmailLog.objects.filter(recipient__iexact=email).delete()
            for booking_id in booking_ids:
                EmailLog.objects.filter(body_text__icontains=booking_id).delete()
            user.delete()
        for invoice_path in invoice_paths:
            file_path = os.path.join(
                settings.MEDIA_ROOT, "invoices", os.path.basename(invoice_path)
            )
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except OSError as exc:
                messages.warning(request, f"Account deleted, but an invoice file could not be removed: {exc}")
        if profile_image:
            try:
                profile_image.delete(save=False)
            except Exception as exc:
                messages.warning(request, f"Account deleted, but its profile image could not be removed: {exc}")
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
        if not user.is_active and user.email:
            try:
                mailer.send_generic_notification(
                    to_email=user.email,
                    subject="Your VOYAGE account has been deactivated",
                    template_path="emails/account_deactivated.html",
                    context={
                        "user_name": user.get_full_name() or user.get_username(),
                        "support_email": settings.DEFAULT_FROM_EMAIL,
                        "_email_event": "account_deactivated",
                    },
                )
            except Exception as exc:
                messages.warning(request, f"Account deactivated, but the notification email could not be sent: {exc}")
        elif user.is_active and user.email:
            try:
                mailer.send_generic_notification(
                    to_email=user.email,
                    subject="Your VOYAGE account has been reactivated",
                    template_path="emails/account_activated.html",
                    context={
                        "user_name": user.get_full_name() or user.get_username(),
                        "support_email": settings.DEFAULT_FROM_EMAIL,
                        "login_url": request.build_absolute_uri(reverse("accounts:login")),
                        "_email_event": "account_activated",
                    },
                )
            except Exception as exc:
                messages.warning(request, f"Account activated, but the notification email could not be sent: {exc}")
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
    tab = request.GET.get("tab", "inbox")
    if tab not in {"inbox", "sent", "contacts"}:
        tab = "inbox"
    query = request.GET.get("q", "").strip()
    inbox_list = _search(
        ContactMessage.objects.filter(is_replied=False),
        query,
        ["name", "email", "subject", "message"],
    )
    contact_list = _search(
        ContactMessage.objects.all(),
        query,
        ["name", "email", "subject", "message"],
    )
    sent_list = _search(
        EmailLog.objects.all(),
        query,
        ["sender", "recipient", "subject", "body_text"],
    )
    page_items = list(
        {"inbox": inbox_list, "sent": sent_list, "contacts": contact_list}[tab]
    )
    if tab in {"inbox", "contacts"}:
        for contact in page_items:
            contact.reply_sender = settings.DEFAULT_FROM_EMAIL
    else:
        from apps.core.utils.mailer import clean_logged_email_text

        for email in page_items:
            email.display_sender = email.sender or settings.DEFAULT_FROM_EMAIL
            email.display_body = clean_logged_email_text(email.body_text)
            if email.body_html:
                from apps.core.utils.mailer import email_html_to_message_text

                email.display_body = email_html_to_message_text(email.body_html)
            if email.event in {
                "account_activated",
                "account_deactivated",
            }:
                account = User.objects.filter(email__iexact=email.recipient).first()
                display_name = (
                    account.get_full_name() or account.get_username()
                    if account
                    else "Traveller"
                )
                if email.event == "account_activated":
                    email.display_body = (
                        f"Account update. Hello {display_name}, "
                        "An administrator has reactivated your VOYAGE account. "
                        "You can now sign in and continue managing your journeys. "
                        f"If you need help, contact {settings.DEFAULT_FROM_EMAIL}."
                    )
                else:
                    email.display_body = (
                        f"Account update. Hello {display_name}, "
                        "your VOYAGE account has been deactivated by an administrator, "
                        "so sign-in is temporarily unavailable. Your booking records "
                        "and payment history remain preserved. Contact our team if you "
                        f"need help: {settings.DEFAULT_FROM_EMAIL}."
                    )
            contact_event_fields = {
                "contact_reply": ("replied_at", "reply_body"),
                "contact_received_customer": ("created_at", "message"),
                "contact_received_admin": ("created_at", "message"),
            }
            event_match = contact_event_fields.get(email.event)
            if event_match and email.sent_at:
                timestamp_field, body_field = event_match
                contact_filters = {
                    f"{timestamp_field}__range": (
                        email.sent_at - timedelta(minutes=5),
                        email.sent_at + timedelta(minutes=5),
                    ),
                }
                if email.event == "contact_reply":
                    contact_filters["email__iexact"] = email.recipient
                    contact_filters.update(
                        reply_subject=email.subject,
                        is_replied=True,
                    )
                elif email.event == "contact_received_admin":
                    contact_filters["subject"] = email.subject.removeprefix(
                        "New contact message: "
                    )
                else:
                    contact_filters["email__iexact"] = email.recipient
                    contact_filters["subject"] = email.subject
                contact_matches = list(
                    ContactMessage.objects.filter(
                        **contact_filters
                    )
                    .exclude(**{body_field: ""})
                )
                if contact_matches:
                    closest_seconds = min(
                        abs(
                            (
                                getattr(contact, timestamp_field)
                                - email.sent_at
                            ).total_seconds()
                        )
                        for contact in contact_matches
                    )
                    closest_matches = [
                        contact
                        for contact in contact_matches
                        if abs(
                            (
                                getattr(contact, timestamp_field)
                                - email.sent_at
                            ).total_seconds()
                        )
                        == closest_seconds
                    ]
                    if len(closest_matches) == 1:
                        email.display_body = getattr(closest_matches[0], body_field)
            if email.event in {"contact_reply", "contact_received_customer"}:
                email.display_html = ""
    return render(
        request,
        "admin_panel/communications_v2.html",
        {
            "active_tab": tab,
            "query": query,
            "contact_messages": page_items if tab in {"inbox", "contacts"} else [],
            "email_logs": page_items if tab == "sent" else [],
            "inbox_count": ContactMessage.objects.filter(is_replied=False).count(),
            "contact_count": ContactMessage.objects.count(),
            "sent_count": EmailLog.objects.count(),
        },
    )


@require_POST
@admin_required
def compose_message(request):
    recipient = request.POST.get("recipient", "").strip()
    subject = request.POST.get("subject", "").strip()
    body = request.POST.get("body", "").strip()
    try:
        validate_email(recipient)
    except ValidationError:
        messages.error(request, "Enter a valid recipient email address.")
        return redirect("admin_panel:communications")
    if not subject or not body:
        messages.error(request, "Add a subject and message before sending.")
        return redirect("admin_panel:communications")
    try:
        mailer.send_admin_message(recipient, subject, body)
    except Exception as exc:
        messages.error(request, f"The message could not be sent: {exc}")
    else:
        messages.success(request, f"Email sent to {recipient}.")
    return redirect(f"{reverse('admin_panel:communications')}?tab=sent")


@require_POST
@admin_required
def reply_to_contact(request, pk):
    contact_message = get_object_or_404(ContactMessage, pk=pk)
    reply_body = request.POST.get("reply_body", "").strip()
    if not reply_body:
        messages.error(request, "Write a reply before sending it.")
        return redirect(f"{reverse('admin_panel:communications')}?tab=contacts")

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
                "_email_log_body": reply_body,
            },
        )
    except Exception as exc:
        messages.error(request, f"The reply could not be sent: {exc}")
    else:
        contact_message.is_replied = True
        contact_message.reply_subject = subject
        contact_message.reply_body = reply_body
        contact_message.replied_at = timezone.now()
        contact_message.save(update_fields=["is_replied", "reply_subject", "reply_body", "replied_at"])
        messages.success(request, f"Reply sent to {contact_message.email}.")
    return redirect(f"{reverse('admin_panel:communications')}?tab=contacts")
