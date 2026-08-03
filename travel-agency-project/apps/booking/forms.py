from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    TRAVEL_STYLE_CHOICES = [
        ('', 'Select your style'),
        ('relaxed', 'Relaxed & Slow-Paced'),
        ('romantic', 'Romantic & Intimate'),
        ('cultural', 'Culture & Heritage'),
        ('adventure', 'Adventure & Discovery'),
        ('luxury', 'Luxury Lifestyle'),
        ('family', 'Family Friendly'),
    ]

    BUDGET_CHOICES = [
        ('', 'Select budget range'),
        ('budget', 'Budget Friendly'),
        ('mid', 'Mid Range'),
        ('premium', 'Premium'),
        ('luxury', 'Luxury'),
        ('ultra', 'Ultra Luxury'),
    ]

    travel_style = forms.ChoiceField(choices=TRAVEL_STYLE_CHOICES, required=False)
    budget_range = forms.ChoiceField(choices=BUDGET_CHOICES, required=False)

    class Meta:
        model = Booking
        fields = ['full_name', 'email', 'phone', 'destination_name', 'travel_date',
                  'num_travelers', 'budget_range', 'travel_style', 'special_requests']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'your@email.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 98765 43210'}),
            'destination_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Where do you want to go?'}),
            'travel_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'num_travelers': forms.NumberInput(attrs={'class': 'form-input', 'min': '1', 'max': '50'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Any special requests or preferences...'}),
        }
