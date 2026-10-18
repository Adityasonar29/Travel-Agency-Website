from django.contrib import admin
from django.db.models import Avg, Sum
from apps.booking.models import Booking, Review
from .models import SiteSettings, Destination, Tour, Experience, FunFact, Testimonial, Stat, MarqueeWord, ContactMessage, EmailLog, Blog, AboutPage




@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_replied')
    list_filter = ('is_replied', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('subject', 'recipient', 'event', 'status', 'created_at', 'sent_at')
    list_filter = ('status', 'event', 'created_at')
    search_fields = ('subject', 'recipient', 'event', 'body_text')
    readonly_fields = ('created_at', 'sent_at')


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):

    fieldsets = (
        (
            "Hero Section",
            {
                "fields": (
                    "hero_overline",
                    "hero_heading",
                    "hero_subheading",
                    "hero_image",
                )
            },
        ),
        (
            "Our Story",
            {
                "fields": (
                    "story_overline",
                    "story_heading",
                    "story_text",
                    "story_image",
                )
            },
        ),
        (
            "Core Values",
            {
                "fields": (
                    "values_heading",

                    "value_one_title",
                    "value_one_text",

                    "value_two_title",
                    "value_two_text",

                    "value_three_title",
                    "value_three_text",
                )
            },
        ),
        (
            "Call To Action",
            {
                "fields": (
                    "cta_heading",
                    "cta_text",
                    "cta_button",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return not AboutPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {'fields': ('site_name', 'tagline')}),
        ('Hero', {'fields': ('hero_video', 'hero_heading_line1', 'hero_heading_line2', 'hero_subtitle', 'hero_cta_text')}),
        ('About', {'fields': ('about_overline', 'about_heading', 'about_text', 'about_image')}),
        ('Contact', {'fields': ('email', 'phone', 'address')}),
        ('Social', {'fields': ('instagram', 'facebook', 'twitter')}),
    )




@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'slug', 'is_featured', 'order')
    list_filter = ('country', 'is_featured')
    list_editable = ('order', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_person', 'duration', 'seats_available', 'is_featured', 'order')
    list_filter = ('is_featured',)
    list_editable = ('order', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('destinations',)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'order')
    list_editable = ('order',)


@admin.register(FunFact)
class FunFactAdmin(admin.ModelAdmin):
    list_display = ('title', 'emoji', 'order')
    list_editable = ('order',)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'author_destination', 'is_active', 'order')
    list_filter = ('is_active',)
    list_editable = ('order', 'is_active')


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ('label', 'metric', 'display_stat_value', 'suffix', 'order')
    list_editable = ('metric', 'suffix', 'order')

    @admin.display(description="Website value")
    def display_stat_value(self, obj):
        if obj.metric == "manual":
            return f"{obj.prefix}{obj.value}{obj.suffix}"
        if obj.metric == "satisfaction":
            average = Review.objects.aggregate(value=Avg("rating"))["value"]
            value = round(average / 5 * 100) if average is not None else obj.value
            return f"{value}%"
        if obj.metric == "tours":
            return Tour.objects.count()
        if obj.metric == "destinations":
            return Destination.objects.count()
        if obj.metric == "travelers":
            return (
                Booking.objects.filter(status__in=["confirmed", "completed"]).aggregate(
                    total=Sum("num_travelers")
                )["total"]
                or 0
            )
        return f"{obj.prefix}{obj.value}{obj.suffix}"


@admin.register(MarqueeWord)
class MarqueeWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'order')
    list_editable = ('order',)
