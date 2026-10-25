import logging
import secrets
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.conf import settings
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.utils import timezone
from .forms import (
    LoginForm,
    PasswordResetRequestForm,
    PasswordResetVerifyForm,
    ProfileForm,
    RegisterForm,
)
from apps.booking.models import Booking
from apps.booking.views import _update_completed_bookings
from apps.accounts.models import PasswordResetPin, WishlistItem
from apps.core.models import Destination, Tour
from apps.core.utils import mailer

User = get_user_model()
logger = logging.getLogger(__name__)
PASSWORD_RESET_SESSION_KEY = "password_reset_user_id"
PASSWORD_RESET_PIN_LIFETIME = timedelta(minutes=10)
PASSWORD_RESET_RESEND_DELAY = timedelta(seconds=60)
PASSWORD_RESET_MAX_ATTEMPTS = 5


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get('email')
            user.save()
            messages.success(request, 'Account created. Please log in.')
            return redirect('accounts:login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('core:home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']
            remember = form.cleaned_data.get('remember_me')

            # allow login via email or username
            user = None
            try:
                user_obj = User.objects.filter(email__iexact=identifier).first()
                if user_obj:
                    username = user_obj.get_username()
                    user = authenticate(request, username=username, password=password)
                else:
                    user = authenticate(request, username=identifier, password=password)
            except Exception:
                user = authenticate(request, username=identifier, password=password)

            inactive_user = User.objects.filter(
                email__iexact=identifier,
                is_active=False,
            ).first() or User.objects.filter(
                username=identifier,
                is_active=False,
            ).first()
            if user is None and inactive_user and inactive_user.check_password(password):
                messages.error(
                    request,
                    'This VOYAGE account is deactivated. Please contact support to restore access.',
                )
                return render(request, 'accounts/login.html', {'form': form, 'next': next_url})

            if user is not None:
                login(request, user)
                if remember:
                    request.session.set_expiry(60 * 60 * 24 * 30)
                else:
                    request.session.set_expiry(0)

                if user.email:
                    try:
                        mailer.send_login_alert(
                            user.email,
                            {
                                'user_name': user.get_full_name() or user.get_username(),
                                'login_time': timezone.localtime().strftime('%d %b %Y, %I:%M %p'),
                                'ip_address': request.META.get('REMOTE_ADDR') or 'Unavailable',
                                'device': request.META.get('HTTP_USER_AGENT', 'Browser sign-in')[:180],
                                'profile_url': request.build_absolute_uri(reverse('accounts:profile')),
                            },
                        )
                    except Exception:
                        # A mail server outage must never prevent a valid login.
                        logger.exception("Login alert email delivery failed.")

                messages.success(request, "You are now logged in.")

                # Admin goes to dashboard
                if user.is_staff or user.is_superuser:
                    return redirect("admin_panel:dashboard")

                return redirect(next_url)
            else:
                messages.error(request, 'Invalid credentials')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def forgot_password_view(request):
    form = PasswordResetRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        identifier = form.cleaned_data["username_or_email"].strip()
        user = User.objects.filter(
            email__iexact=identifier,
            is_active=True,
        ).first() or User.objects.filter(
            username__iexact=identifier,
            is_active=True,
        ).first()

        request.session.pop(PASSWORD_RESET_SESSION_KEY, None)
        if user and user.email:
            reset_pin, created = PasswordResetPin.objects.get_or_create(
                user=user,
                defaults={
                    "pin_hash": "",
                    "expires_at": timezone.now(),
                },
            )
            now = timezone.now()
            if (
                created
                or reset_pin.expires_at <= now
                or reset_pin.created_at < now - PASSWORD_RESET_RESEND_DELAY
            ):
                pin = f"{secrets.randbelow(1_000_000):06d}"
                reset_pin.pin_hash = make_password(pin)
                reset_pin.created_at = now
                reset_pin.expires_at = now + PASSWORD_RESET_PIN_LIFETIME
                reset_pin.attempts = 0
                reset_pin.save(
                    update_fields=[
                        "pin_hash",
                        "created_at",
                        "expires_at",
                        "attempts",
                    ]
                )
                try:
                    mailer.send_generic_notification(
                        user.email,
                        "Your VOYAGE password reset PIN",
                        "emails/password_reset_pin.html",
                        {
                            "user_name": user.get_full_name() or user.get_username(),
                            "pin": pin,
                            "expires_minutes": int(
                                PASSWORD_RESET_PIN_LIFETIME.total_seconds() // 60
                            ),
                            "support_email": settings.DEFAULT_FROM_EMAIL,
                            "_email_event": "password_reset_pin",
                        },
                    )
                except Exception:
                    reset_pin.delete()
                    logger.exception(
                        "Unable to send password reset PIN to account %s",
                        user.pk,
                    )
                    messages.error(
                        request,
                        "We could not send the reset email right now. Please try again later.",
                    )
                    return render(
                        request,
                        "accounts/forgot_password.html",
                        {"form": form},
                    )
            request.session[PASSWORD_RESET_SESSION_KEY] = user.pk

        messages.success(
            request,
            "If an active account matches those details, a password reset PIN has been sent to its email address.",
        )
        return redirect("accounts:reset_password")

    return render(request, "accounts/forgot_password.html", {"form": form})


def reset_password_view(request):
    user_id = request.session.get(PASSWORD_RESET_SESSION_KEY)
    user = User.objects.filter(pk=user_id, is_active=True).first() if user_id else None
    if user is None:
        messages.info(request, "Request a password reset PIN to continue.")
        return redirect("accounts:forgot_password")

    form = PasswordResetVerifyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        reset_pin = PasswordResetPin.objects.filter(user=user).first()
        if reset_pin is None or reset_pin.attempts >= PASSWORD_RESET_MAX_ATTEMPTS:
            messages.error(
                request,
                "That PIN has expired or is no longer valid. Request a new one.",
            )
            request.session.pop(PASSWORD_RESET_SESSION_KEY, None)
            return redirect("accounts:forgot_password")

        if reset_pin.expires_at <= timezone.now():
            reset_pin.delete()
            request.session.pop(PASSWORD_RESET_SESSION_KEY, None)
            messages.error(
                request,
                "That PIN has expired. Request a new one to continue.",
            )
            return redirect("accounts:forgot_password")

        if not check_password(form.cleaned_data["pin"], reset_pin.pin_hash):
            reset_pin.attempts += 1
            if reset_pin.attempts >= PASSWORD_RESET_MAX_ATTEMPTS:
                reset_pin.delete()
                request.session.pop(PASSWORD_RESET_SESSION_KEY, None)
                messages.error(
                    request,
                    "Too many incorrect attempts. Request a new PIN to continue.",
                )
                return redirect("accounts:forgot_password")
            reset_pin.save(update_fields=["attempts"])
            form.add_error("pin", "That PIN is incorrect.")
            return render(request, "accounts/reset_password.html", {"form": form})

        new_password = form.cleaned_data["new_password1"]
        try:
            validate_password(new_password, user=user)
        except ValidationError as exc:
            form.add_error("new_password1", exc)
            return render(request, "accounts/reset_password.html", {"form": form})

        user.set_password(new_password)
        user.save(update_fields=["password"])
        reset_pin.delete()
        request.session.pop(PASSWORD_RESET_SESSION_KEY, None)
        messages.success(request, "Your password has been reset. You can now log in.")
        return redirect("accounts:login")

    return render(request, "accounts/reset_password.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:home')


@login_required
def profile_view(request):
    user = request.user
    profile_form = ProfileForm(request.POST or None, request.FILES or None, instance=user)
    password_form = PasswordChangeForm(user=user, data=request.POST or None)

    _update_completed_bookings(request.user)
    
    bookings = user.bookings.select_related('tour').all()
    
    for booking in bookings:
        booking.update_completion_status()
    wishlist_items = user.wishlist_items.select_related('destination', 'tour').all()

    if request.method == 'POST':
        if 'save_profile' in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Please fix the issues in your profile.')
        elif 'change_password' in request.POST:
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been updated.')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Please correct the password form errors.')

    upcoming_count = bookings.filter(status__in=['pending', 'confirmed']).count()
    favorites_count = wishlist_items.count()
    profile_fields = (
        user.first_name,
        user.last_name,
        user.email,
        user.phone,
        user.country,
        user.profile_image,
    )
    profile_completion = round(
        sum(bool(value) for value in profile_fields)
        / len(profile_fields)
        * 100
    )

    return render(request, 'accounts/profile.html', {
        'form': profile_form,
        'password_form': password_form,
        'user': user,
        'bookings': bookings,
        'wishlist_items': wishlist_items,
        'upcoming_count': upcoming_count,
        'favorites_count': favorites_count,
        'profile_completion': profile_completion,
    })


@login_required
def toggle_wishlist(request):
    destination_id = request.GET.get('destination')
    tour_id = request.GET.get('tour')
    redirect_to = request.GET.get('next') or request.META.get('HTTP_REFERER') or reverse('accounts:profile')

    if destination_id:
        destination = get_object_or_404(Destination, pk=destination_id)
        item, created = WishlistItem.objects.get_or_create(user=request.user, destination=destination)
        if not created:
            item.delete()
            messages.info(request, f'Removed {destination.name} from your wishlist.')
        else:
            messages.success(request, f'Added {destination.name} to your wishlist.')
    elif tour_id:
        tour = get_object_or_404(Tour, pk=tour_id)
        item, created = WishlistItem.objects.get_or_create(user=request.user, tour=tour)
        if not created:
            item.delete()
            messages.info(request, f'Removed {tour.name} from your wishlist.')
        else:
            messages.success(request, f'Added {tour.name} to your wishlist.')
    else:
        messages.error(request, 'Unable to update wishlist item.')

    return redirect(redirect_to)


@login_required
def remove_wishlist_item(request, pk):
    item = get_object_or_404(WishlistItem, pk=pk, user=request.user)
    item_name = item.destination.name if item.destination else item.tour.name if item.tour else 'item'
    item.delete()
    messages.info(request, f'Removed {item_name} from your wishlist.')
    return redirect(request.GET.get('next') or request.META.get('HTTP_REFERER') or reverse('accounts:profile'))
