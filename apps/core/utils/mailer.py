import os
import re
from email.mime.image import MIMEImage
from email.utils import parseaddr
from html import unescape
from html.parser import HTMLParser

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils import timezone


class _EmailTextParser(HTMLParser):
    _BLOCK_TAGS = {
        "address", "article", "blockquote", "br", "dd", "dl", "dt",
        "footer", "h1", "h2", "h3", "h4", "header", "li", "ol", "p",
        "section", "table", "td", "th", "tr", "ul",
    }
    _IGNORED_TAGS = {"head", "script", "style"}

    def __init__(self, body_only=False):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.ignored_depth = 0
        self.body_only = body_only
        self.in_message_body = False
        self.message_table_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self._IGNORED_TAGS:
            self.ignored_depth += 1
            return
        if self.body_only and tag == "td":
            classes = dict(attrs).get("class", "").split()
            if not self.in_message_body and "body" in classes:
                self.in_message_body = True
                self.message_table_depth = 1
            elif self.in_message_body:
                self.message_table_depth += 1
        if (
            not self.ignored_depth
            and (not self.body_only or self.in_message_body)
            and tag in self._BLOCK_TAGS
        ):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self._IGNORED_TAGS and self.ignored_depth:
            self.ignored_depth -= 1
            return
        if (
            self.body_only
            and self.in_message_body
            and tag == "td"
        ):
            self.message_table_depth -= 1
            if self.message_table_depth == 0:
                self.in_message_body = False
        if (
            not self.ignored_depth
            and (not self.body_only or self.in_message_body)
            and tag in self._BLOCK_TAGS
        ):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.ignored_depth and (
            not self.body_only or self.in_message_body
        ):
            self.parts.append(data)


def email_html_to_text(html_content):
    return _email_html_to_text(html_content)


def email_html_to_message_text(html_content):
    return _email_html_to_text(html_content, body_only=True)


def _email_html_to_text(html_content, body_only=False):
    parser = _EmailTextParser(body_only=body_only)
    parser.feed(html_content)
    text = re.sub(r"[ \t]+\n", "\n", "".join(parser.parts))
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def clean_logged_email_text(text):
    text = (text or "").strip()
    if "<" in text and ">" in text:
        text = email_html_to_message_text(text)

    css_match = re.search(
        r"(?:^|\s)(?:body|html|table|@media|\.[A-Za-z_][\w-]*)\s*\{",
        text,
        re.IGNORECASE,
    )
    if css_match:
        prefix = text[:css_match.start()].strip()
        brand_match = re.search(
            r"VOYAGE\s*Travel agency\s*[·.-]\s*thoughtfully arranged",
            text[css_match.end():],
            re.IGNORECASE,
        )
        if brand_match:
            text = text[css_match.end() + brand_match.end():]
        else:
            css_end = text.rfind("}")
            suffix = text[css_end + 1:].strip() if css_end >= css_match.end() else ""
            text = " ".join(part for part in (prefix, suffix) if part)

    text = unescape(text)
    text = re.sub(
        r"^(?:VOYAGE\s*)?(?:Travel agency\s*[·.-]\s*thoughtfully arranged\s*)?",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"^(?:Message received|Account update)\s*", "", text, flags=re.IGNORECASE)
    text = re.split(r"Need help\?\s*Contact\b", text, maxsplit=1, flags=re.IGNORECASE)[0]
    return re.sub(r"\s+", " ", text).strip()


def _send_html_email(subject, to_email, template_path, context=None, attachments=None):
    context = context or {}
    template_context = dict(context)
    event = template_context.pop('_email_event', '') or template_path.rsplit('/', 1)[-1].replace('.html', '')
    log_body = template_context.pop('_email_log_body', None)
    html_content = render_to_string(template_path, template_context)
    text_content = email_html_to_text(html_content)
    message_content = email_html_to_message_text(html_content)
    sender_email = parseaddr(settings.DEFAULT_FROM_EMAIL)[1] or settings.EMAIL_HOST_USER

    email_log = None
    try:
        from apps.core.models import EmailLog
        email_log = EmailLog.objects.create(
            sender=sender_email,
            recipient=to_email,
            subject=subject,
            template_path=template_path,
            event=event,
            body_text=log_body if log_body is not None else message_content,
            body_html=html_content,
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


def send_admin_message(to_email, subject, body):
    sender_email = parseaddr(settings.DEFAULT_FROM_EMAIL)[1] or settings.EMAIL_HOST_USER
    email_log = None
    try:
        from apps.core.models import EmailLog
        email_log = EmailLog.objects.create(
            sender=sender_email,
            recipient=to_email,
            subject=subject,
            event="admin_composed",
            body_text=body,
            status="sent",
        )
    except Exception:
        email_log = None

    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=False)
    except Exception as exc:
        if email_log:
            email_log.status = "failed"
            email_log.error_message = str(exc)
            email_log.save(update_fields=["status", "error_message"])
        raise
    if email_log:
        email_log.sent_at = timezone.now()
        email_log.save(update_fields=["sent_at"])


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
