from .models import SiteSettings, Destination


def site_settings(request):
    try:
        settings = SiteSettings.load()
    except Exception:
        settings = None
    return {'site_settings': settings}




def footer_destinations_processor(request):
    
    # This fetches the top 5 destinations to keep the footer layout clean
    return {
        'footer_destinations': Destination.objects.all()[:5]
    }