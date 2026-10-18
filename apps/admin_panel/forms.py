from django import forms

from apps.core.models import Destination, Tour


class AdminModelForm(forms.ModelForm):
    """Shared styling hooks for the custom dashboard forms."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "field-control")


class TourForm(AdminModelForm):
    class Meta:
        model = Tour
        fields = [
            "name", "summary", "destinations", "duration", "duration_days",
            "price_per_person", "budget_range", "seats_available", "max_capacity",
            "overview", "hero_image", "image", "rating", "is_featured", "order",
        ]
        widgets = {
            "destinations": forms.SelectMultiple(attrs={"class": "field-control field-multiple"}),
            "overview": forms.Textarea(attrs={"rows": 5}),
            "price_per_person": forms.NumberInput(attrs={"step": "0.01"}),
            "rating": forms.NumberInput(attrs={"step": "0.1", "min": "0", "max": "5"}),
        }


class DestinationForm(AdminModelForm):
    class Meta:
        model = Destination
        fields = [
            "name", "country", "state", "city", "description", "image", "hover_image",
            "hero_image", "best_time_to_travel", "weather", "rating", "latitude",
            "longitude", "is_featured", "order",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "rating": forms.NumberInput(attrs={"step": "0.1", "min": "0", "max": "5"}),
        }
