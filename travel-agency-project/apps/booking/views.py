from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BookingForm


def booking_page(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your booking request has been submitted! We will contact you shortly.')
            return redirect('core:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm()

    return render(request, 'pages/booking.html', {'form': form})
