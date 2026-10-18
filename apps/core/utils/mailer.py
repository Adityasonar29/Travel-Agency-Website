from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
import os
from email.mime.image import MIMEImage


def _send_html_email(subject, to_email, template_path, context=None, attachments=None):
    context = context or {}
    template_context = dict(context)
    event = template_context.pop('_email_event', '') or template_path.rsplit('/', 1)[-1].replace('.html', '')
    html_content = render_to_string(template_path, template_context)
    text_content = strip_tags(html_content)

    email_log = None
    try:
        from apps.core.models import EmailLog
        email_log = EmailLog.objects.create(
            recipient=to_email,
            subject=subject,
            template_path=template_path,
            event=event,
            body_text=text_content,
            status='sent',
        )
    except Exception:
        email_log = None

    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [to_email])
    msg.attach_alternative(html_content, "text/html")

    logo_path = os.path.join(settings.BASE_DIR, "static", "images", "voyage-logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as logo_file:
            logo = MIMEImage(logo_file.read(), _subtype="png")
        logo.add_header("Content-ID", "<voyage-logo>")
        logo.add_header("Content-Disposition", "inline", filename="voyage-logo.png")
        msg.attach(logo)

    # Attach files if provided (list of file paths)
    if attachments:
        for path in attachments:
            if path and os.path.exists(path):
                msg.attach_file(path)

    try:
        msg.send(fail_silently=False)
    except Exception as exc:
        if email_log:
            email_log.status = 'failed'
            email_log.error_message = str(exc)
            email_log.save(update_fields=['status', 'error_message'])
        raise
    if email_log:
        email_log.sent_at = timezone.now()
        email_log.save(update_fields=['sent_at'])


def send_booking_confirmation(to_email, context):
    """Send booking confirmation email. Context should contain keys used by template."""
    subject = context.get('subject', 'Your Booking Confirmation')
    template = 'emails/booking_confirmation.html'
    attachments = context.get('attachments')  # optional list of file paths
    _send_html_email(subject, to_email, template, context, attachments)


def send_admin_booking_notification(to_email, context):
    """Send admin notification when a new booking is created."""
    subject = f"New Booking #{context.get('booking_id', '')} - {context.get('customer_name', '')}"
    template = 'emails/admin_booking_notification.html'
    _send_html_email(subject, to_email, template, context)


def send_contact_auto_reply(to_email, context):
    subject = context.get('subject', 'Thanks for contacting Voyage')
    template = 'emails/contact_auto_reply.html'
    _send_html_email(subject, to_email, template, context)

def send_welcome_email(to_email, context):
    subject = context.get('subject', 'Welcome to Voyage')
    template = 'emails/welcome.html'
    _send_html_email(subject, to_email, template, context)


def send_login_alert(to_email, context):
    """Notify a traveller when their account is successfully accessed."""
    subject = context.get('subject', 'A new sign-in to your VOYAGE account')
    _send_html_email(subject, to_email, 'emails/login_alert.html', context)


# Generic helper for other notifications
def send_generic_notification(to_email, subject, template_path, context=None, attachments=None):
    _send_html_email(subject, to_email, template_path, context or {}, attachments)
