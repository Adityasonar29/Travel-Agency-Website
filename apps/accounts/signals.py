from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from core.utils.mailer import send_welcome_email



# Placeholder for any account-related signals (e.g., send welcome email)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def user_post_save(sender, instance, created, **kwargs):
    if created:
        send_welcome_email(
            instance.email,
            {
                'user': instance,
                'user_name': instance.get_full_name() or instance.get_username(),
            },
        )
