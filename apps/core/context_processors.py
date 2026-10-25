from django.conf import settings
from django.db.models import Avg, Sum

from apps.booking.models import Booking, Review
from .models import Destination, SiteSettings, Stat, Tour


def debug_mode(request):
    return {"debug_mode": settings.DEBUG}


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


def site_stats_processor(request):
    public_metrics = ("destinations", "travelers", "satisfaction", "tours")
    stats_by_metric = {
        stat.metric: stat
        for stat in Stat.objects.filter(metric__in=public_metrics)
    }
    stats = [
        stats_by_metric[metric]
        for metric in public_metrics
        if metric in stats_by_metric
    ]
    review_average = Review.objects.aggregate(value=Avg("rating"))["value"]
    totals = {
        "tours": Tour.objects.count(),
        "destinations": Destination.objects.count(),
        "travelers": (
            Booking.objects.filter(status__in=["confirmed", "completed"]).aggregate(
                total=Sum("num_travelers")
            )["total"]
            or 0
        ),
        "satisfaction": (
            round(review_average / 5 * 100)
            if review_average is not None
            else None
        ),
    }
    for stat in stats:
        if stat.metric == "manual":
            stat.display_value = f"{stat.prefix}{stat.value}{stat.suffix}"
        elif stat.metric == "satisfaction":
            satisfaction = totals["satisfaction"]
            stat.display_value = (
                f"{satisfaction}%"
                if satisfaction is not None
                else f"{stat.prefix}{stat.value}{stat.suffix}"
            )
        else:
            stat.display_value = str(totals[stat.metric])
    return {
        "site_stats": stats,
    }