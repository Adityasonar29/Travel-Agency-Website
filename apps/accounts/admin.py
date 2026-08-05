from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, WishlistItem


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Additional', {'fields': ('phone', 'profile_image', 'country', 'is_verified', 'notification_emails', 'notification_sms')}),
    )


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'destination', 'tour', 'created_at')
    search_fields = ('user__username', 'destination__name', 'tour__name')
    list_filter = ('created_at',)
