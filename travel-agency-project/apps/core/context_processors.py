from .models import SiteSettings


def site_settings(request):
    try:
        settings = SiteSettings.load()
    except Exception:
        settings = None
    return {'site_settings': settings}
