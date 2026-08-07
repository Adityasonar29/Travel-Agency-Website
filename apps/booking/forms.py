from django import forms
from apps.core.models import Tour, Destination
from .models import Booking


class TourModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        destination = obj.destinations.first()
        if destination:
            return f"{obj.name} — {destination.name}"
        return obj.name


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
        ('budget', 'Budget Friendly — Rs. 25,000-45,000'),
        ('mid', 'Mid Range — Rs. 45,000-75,000'),
        ('premium', 'Premium — Rs. 75,000-1,20,000'),
        ('luxury', 'Luxury — Rs. 1,20,000-2,50,000'),
        ('ultra', 'Ultra Luxury — Rs. 2,50,000+'),
    ]

    destination_name = forms.ChoiceField(
        choices=[], required=True, label='Destination',
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    tour = TourModelChoiceField(
        queryset=Tour.objects.none(), required=True,
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    travel_style = forms.ChoiceField(
        choices=TRAVEL_STYLE_CHOICES, required=False,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    budget_range = forms.ChoiceField(
        choices=BUDGET_CHOICES, required=False,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    num_travelers = forms.IntegerField(
        min_value=1, max_value=50, initial=2,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '2'})
    )

    class Meta:
        model = Booking
        fields = ['tour', 'destination_name', 'full_name', 'email', 'phone', 'travel_date',
                  'num_travelers', 'budget_range', 'travel_style', 'special_requests']
        widgets = {
            'tour': forms.Select(attrs={'class': 'form-input'}),
            'destination_name': forms.Select(attrs={'class': 'form-input'}),
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'your@email.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 98765 43210'}),
            'travel_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Any special requests or preferences...'}),
        }

    def __init__(self, *args, **kwargs):
        initial_tour = kwargs.pop('initial_tour', None)
        super().__init__(*args, **kwargs)

        destinations = Destination.objects.all()
        destination_choices = [('', 'Select destination')]
        for dest in destinations:
            destination_choices.append((dest.name, dest.name))
        self.fields['destination_name'].choices = destination_choices

        self.fields['tour'].queryset = Tour.objects.all().order_by('name')
        self.fields['tour'].empty_label = 'Select a tour'

        if initial_tour:
            self.fields['tour'].initial = initial_tour
            first_dest = initial_tour.destinations.first()
            if first_dest:
                self.fields['destination_name'].initial = first_dest.name
