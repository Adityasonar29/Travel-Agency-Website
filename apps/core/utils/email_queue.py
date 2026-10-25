import logging
import os
from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone

from apps.core.models import EmailLog, OutboundEmail
from apps.booking.models import Booking

logger = logging.getLogger(__name__)

_DELIVERY_LEASE = timedelta(minutes=5)
_MAX_RETRY_DELAY_SECONDS = 60 * 60


def process_next_email():
    """Claim and deliver one due email, retrying failures with backoff."""
    now = timezone.now()
    eligible = (
        Q(status="queued", available_at__lte=now)
        | Q(status="sending", locked_until__lte=now)
        | Q(status="sending", locked_until__isnull=True)
    )
    email_id = (
        OutboundEmail.objects.filter(eligible)
        .order_by("available_at", "created_at")
        .values_list("pk", flat=True)
        .first()
    )
    if email_id is None:
        return False

    claimed = OutboundEmail.objects.filter(pk=email_id).filter(eligible).update(
        status="sending",
        locked_until=now + _DELIVERY_LEASE,
        attempts=F("attempts") + 1,
    )
    if not claimed:
        return False

    queued_email = OutboundEmail.objects.select_related("email_log").get(pk=email_id)
    try:
        message = EmailMultiAlternatives(
            queued_email.subject,
            queued_email.body_text,
            queued_email.sender or settings.DEFAULT_FROM_EMAIL,
            [queued_email.recipient],
        )
        if queued_email.body_html:
            message.attach_alternative(queued_email.body_html, "text/html")

            logo_path = os.path.join(settings.BASE_DIR, "static", "images", "voyage-logo.png")
            if os.path.exists(logo_path):
                from email.mime.image import MIMEImage

                with open(logo_path, "rb") as logo_file:
                    logo = MIMEImage(logo_file.read(), _subtype="png")
                logo.add_header("Content-ID", "<voyage-logo>")
                logo.add_header("Content-Disposition", "inline", filename="voyage-logo.png")
                message.attach(logo)

        for attachment_path in queued_email.attachment_paths:
            if not os.path.isfile(attachment_path):
                raise FileNotFoundError(
                    f"Queued email attachment does not exist: {attachment_path}"
                )
            message.attach_file(attachment_path)

        sent_count = message.send(fail_silently=False)
        if sent_count != 1:
            raise RuntimeError(
                f"Email backend reported {sent_count} delivered messages."
            )
    except Exception as exc:
        retry_delay = min(
            60 * (2 ** min(queued_email.attempts - 1, 6)),
            _MAX_RETRY_DELAY_SECONDS,
        )
        retry_at = timezone.now() + timedelta(seconds=retry_delay)
        OutboundEmail.objects.filter(pk=email_id).update(
            status="queued",
            available_at=retry_at,
            locked_until=None,
            last_error=str(exc),
        )
        if queued_email.email_log_id:
            EmailLog.objects.filter(pk=queued_email.email_log_id).update(
                status="pending",
                error_message=str(exc),
            )
        logger.exception(
            "Email delivery failed for %s (subject=%r, queue_id=%s, attempt=%s); "
            "retry scheduled for %s.",
            queued_email.recipient,
            queued_email.subject,
            email_id,
            queued_email.attempts,
            retry_at.isoformat(),
        )
        return True

    sent_at = timezone.now()
    with transaction.atomic():
        OutboundEmail.objects.filter(pk=email_id).update(
            status="sent",
            locked_until=None,
            last_error="",
            sent_at=sent_at,
        )
        if queued_email.email_log_id:
            EmailLog.objects.filter(pk=queued_email.email_log_id).update(
                status="sent",
                error_message="",
                sent_at=sent_at,
            )
        if queued_email.booking_id:
            booking_update = {
                "invoice_status": "sent",
                "invoice_sent_at": sent_at,
            }
            bookings = Booking.objects.filter(pk=queued_email.booking_id)
            if queued_email.attachment_paths:
                bookings = bookings.filter(
                    invoice_pdf_path__in=queued_email.attachment_paths
                )
            bookings.update(**booking_update)
    logger.info(
        "Email sent to %s (subject=%r, queue_id=%s, attempt=%s).",
        queued_email.recipient,
        queued_email.subject,
        email_id,
        queued_email.attempts,
    )
    return True
