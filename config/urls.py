from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import custom_404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls'), name='home'),
    path('booking/', include('apps.booking.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('dashboard/',include('apps.admin_panel.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Keep this last so valid URLs and development static files resolve first.
urlpatterns += [
    path('<path:unmatched_path>', custom_404, name='custom_404'),
]

handler404 = 'apps.core.views.custom_404'
