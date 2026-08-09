from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from .forms import RegisterForm, LoginForm, ProfileForm
from apps.booking.models import Booking
from apps.booking.views import _update_completed_bookings
from apps.accounts.models import WishlistItem
from apps.core.models import Destination, Tour

User = get_user_model()


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

            if user is not None:
                login(request, user)
                if remember:
                    request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
                else:
                    request.session.set_expiry(0)  # browser session
                messages.success(request, 'You are now logged in.')
                if user is not None:
                    login(request, user)
                
                    if remember:
                        request.session.set_expiry(60 * 60 * 24 * 30)
                    else:
                        request.session.set_expiry(0)
                
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
    profile_completion = 55 + int(bool(user.phone)) * 10 + int(bool(user.country)) * 10 + int(bool(user.profile_image)) * 10
    profile_completion = min(profile_completion, 100)

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
