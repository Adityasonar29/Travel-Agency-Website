from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings


# Placeholder for any account-related signals (e.g., send welcome email)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def user_post_save(sender, instance, created, **kwargs):
    if created:
        # future: send welcome mail
        pass
