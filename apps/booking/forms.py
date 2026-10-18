from array import typecodes

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
        ('budget', 'Budget Friendly — $300-550'),
        ('mid', 'Mid Range — $550-900'),
        ('premium', 'Premium — $900-1,450'),
        ('luxury', 'Luxury — $1,450-3,000'),
        ('ultra', 'Ultra Luxury — $3,000+'),
    ]

    request_type = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    destination_name = forms.CharField(
        required=False,
        label='Destination',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Search or enter a destination...',
            'list': 'destination-options',
            'autocomplete': 'off',
        })
    )

    tour = TourModelChoiceField(
        queryset=Tour.objects.none(), required=False,
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
        min_value=1, max_value=50, initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'min': '1', 'readonly': 'readonly', 'placeholder': '1'})
    )

    origin = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            
            'class': 'form-input',
            'placeholder': 'Where will you be travelling from?'
        })
    )

    return_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
    )

    flexible_dates = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'custom-checkbox'
        })
    )

    adults = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=50,
        initial=1,
        widget=forms.NumberInput(attrs={
            'type': 'number',
            'class': 'form-input',
            'min': '0',
            'max': '50'
        })
    )

    children = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=50,
        initial=0,
        widget=forms.NumberInput(attrs={
            'type': 'number',
            'class': 'form-input',
            'min': '0',
            'max': '50'
        })
    )

    trip_purpose = forms.ChoiceField(
        choices=[
            ('', 'Select trip purpose'),
            ('leisure', 'Leisure'),
            ('honeymoon', 'Honeymoon'),
            ('family', 'Family Holiday'),
            ('anniversary', 'Anniversary'),
            ('birthday', 'Birthday'),
            ('adventure', 'Adventure'),
            ('business', 'Business'),
            ('other', 'Other'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )

    accommodation = forms.ChoiceField(
        choices=[
            ('', 'Select accommodation preference'),
            ('budget', 'Comfortable & Practical'),
            ('4star', 'Premium 4-Star'),
            ('5star', 'Luxury 5-Star'),
            ('boutique', 'Boutique & Character'),
            ('villa', 'Private Villa / Residence'),
            ('flexible', 'Open to Recommendations'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )

    transport_preferences = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 3,
            'placeholder': 'Private transfers, trains, rental car, flights, etc.'
        })
    )

    experience_preferences = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 3,
            'placeholder': 'Food, culture, beaches, adventure, shopping, photography...'
        })
    )

    dietary_requirements = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 2,
            'placeholder': 'Vegetarian, allergies, halal, etc.'
        })
    )

    accessibility_requirements = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 2,
            'placeholder': 'Anything our travel designer should know?'
        })
    )

    additional_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 6,
            'placeholder': 'Describe your ideal trip in your own words...'
        })
    )

    contact_preference = forms.ChoiceField(
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone Call'),
            ('whatsapp', 'WhatsApp'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input'
        })
    )

    class Meta:
        model = Booking
        fields = [
            'tour',
            'destination_name',
            'full_name',
            'email',
            'phone',
            'origin',
            'travel_date',
            'return_date',
            'flexible_dates',
            'num_travelers',
            'adults',
            'children',
            'trip_purpose',
            'budget_range',
            'travel_style',
            'accommodation',
            'transport_preferences',
            'experience_preferences',
            'dietary_requirements',
            'accessibility_requirements',
            'special_requests',
            'additional_notes',
            'contact_preference',
        ]
        widgets = {
            'tour': forms.Select(attrs={'class': 'form-input'}),
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'your@email.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 98765 43210'}),
            'travel_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Any special requests or preferences...'}),
        }


    def clean(self):
        cleaned_data = super().clean()

        request_type = cleaned_data.get('request_type')
        destination = cleaned_data.get('destination_name')
        tour = cleaned_data.get('tour')

        if request_type == 'curated':
            if not destination:
                self.add_error(
                    'destination_name',
                    'Please select a destination.'
                )

            if not tour:
                self.add_error(
                    'tour',
                    'Please select a tour package.'
                )

        elif request_type == 'personalized':
            # Tour is intentionally optional for personalized journeys.
            # Destination is also optional — the user may not know yet.
            pass

        else:
            # Fallback for older/existing booking links.
            if not destination:
                self.add_error(
                    'destination_name',
                    'Please select a destination.'
                )

            if not tour:
                self.add_error(
                    'tour',
                    'Please select a tour package.'
                )

        return cleaned_data

            
    def __init__(self, *args, **kwargs):
        initial_tour = kwargs.pop('initial_tour', None)
        super().__init__(*args, **kwargs)

        destinations = Destination.objects.all().order_by('name')
        
        self.destination_suggestions = [
            dest.name for dest in destinations
        ]

        self.fields['tour'].queryset = Tour.objects.all().order_by('name')
        self.fields['tour'].empty_label = 'Select a tour'

        if initial_tour:
            self.fields['tour'].initial = initial_tour
            first_dest = initial_tour.destinations.first()
            if first_dest:
                self.fields['destination_name'].initial = first_dest.name
