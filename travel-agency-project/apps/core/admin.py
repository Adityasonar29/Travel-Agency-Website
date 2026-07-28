from django.contrib import admin
from .models import SiteSettings, Destination, Experience, FunFact, Testimonial, Stat, MarqueeWord


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
    list_display = ('name', 'country', 'is_featured', 'order')
    list_filter = ('country', 'is_featured')
    list_editable = ('order', 'is_featured')


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
