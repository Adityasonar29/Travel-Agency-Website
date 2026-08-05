from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
import os


def _send_html_email(subject, to_email, template_path, context=None, attachments=None):
    context = context or {}
    html_content = render_to_string(template_path, context)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [to_email])
    msg.attach_alternative(html_content, "text/html")

    # Attach files if provided (list of file paths)
    if attachments:
        for path in attachments:
            if path and os.path.exists(path):
                msg.attach_file(path)

    msg.send(fail_silently=False)


def send_booking_confirmation(to_email, context):
    """Send booking confirmation email. Context should contain keys used by template."""
    subject = context.get('subject', 'Your Booking Confirmation')
    template = 'emails/booking_confirmation.html'
    attachments = context.get('attachments')  # optional list of file paths
    _send_html_email(subject, to_email, template, context, attachments)


def send_contact_auto_reply(to_email, context):
    subject = context.get('subject', 'Thanks for contacting Voyage')
    template = 'emails/contact_auto_reply.html'
    _send_html_email(subject, to_email, template, context)


# Generic helper for other notifications
def send_generic_notification(to_email, subject, template_path, context=None, attachments=None):
    _send_html_email(subject, to_email, template_path, context or {}, attachments)
