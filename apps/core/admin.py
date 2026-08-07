from django.contrib import admin
from .models import SiteSettings, Destination, Tour, Experience, FunFact, Testimonial, Stat, MarqueeWord, ContactMessage, Blog, AboutPage




@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_replied')
    list_filter = ('is_replied', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)


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
    list_display = ('label', 'value', 'suffix', 'order')
    list_editable = ('value', 'order')


@admin.register(MarqueeWord)
class MarqueeWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'order')
    list_editable = ('order',)
