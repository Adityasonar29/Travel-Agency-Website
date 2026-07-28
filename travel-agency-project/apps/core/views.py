from django.shortcuts import render
from .models import Destination, Experience, FunFact, Testimonial, Stat, MarqueeWord


def home(request):
    destinations = Destination.objects.filter(is_featured=True)[:6]
    experiences = Experience.objects.all()[:4]
    funfacts = FunFact.objects.all()[:6]
    testimonials = Testimonial.objects.filter(is_active=True)
    stats = Stat.objects.all()[:4]
    marquee_words = MarqueeWord.objects.all()[:8]

    if not destinations.exists():
        destinations = _sample_destinations()
    if not experiences.exists():
        experiences = _sample_experiences()
    if not funfacts.exists():
        funfacts = _sample_funfacts()
    if not testimonials.exists():
        testimonials = _sample_testimonials()
    if not stats.exists():
        stats = _sample_stats()
    if not marquee_words.exists():
        marquee_words = _sample_marquee()

    return render(request, 'pages/home.html', {
        'destinations': destinations,
        'experiences': experiences,
        'funfacts': funfacts,
        'testimonials': testimonials,
        'stats': stats,
        'marquee_words': marquee_words,
        'show_loading': True,  # Only home page gets loading screen
    })


def destinations_page(request):
    destinations = Destination.objects.all()
    if not destinations.exists():
        destinations = _sample_destinations()
    return render(request, 'pages/destinations.html', {
        'destinations': destinations,
        'show_loading': False,
    })


def about_page(request):
    return render(request, 'pages/about.html', {'show_loading': False})


def contact_page(request):
    return render(request, 'pages/contact.html', {'show_loading': False})


# ── Sample fallback data ──

class _S:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

def _sample_destinations():
    return [
        _S(name='Santorini', country='Greece', image='https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&q=80', hover_image='https://images.unsplash.com/photo-1533105079780-92b9be482077?w=800&q=80', description=''),
        _S(name='Amalfi Coast', country='Italy', image='https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=800&q=80', hover_image='https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=800&q=80', description=''),
        _S(name='Bali', country='Indonesia', image='https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&q=80', hover_image='https://images.unsplash.com/photo-1518548419970-58e3b4079ab2?w=800&q=80', description=''),
        _S(name='Paris', country='France', image='https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80', hover_image='https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=800&q=80', description=''),
        _S(name='Kyoto', country='Japan', image='https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80', hover_image='https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=800&q=80', description=''),
        _S(name='Tuscany', country='Italy', image='https://images.unsplash.com/photo-1516483638261-f4dbaf036963?w=800&q=80', hover_image='https://images.unsplash.com/photo-1529260830199-42c24126f198?w=800&q=80', description=''),
    ]

def _sample_experiences():
    return [
        _S(title='Private Yacht Cruises', subtitle='LUXURY ON WATER', description='Sail through crystal-clear waters aboard a private yacht, with a personal crew catering to your every whim.', image='https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=1200&q=80', link='#'),
        _S(title='Mountain Retreats', subtitle='ELEVATED ESCAPES', description='Find solace in the mountains with curated retreats that blend adventure and tranquility.', image='https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1200&q=80', link='#'),
        _S(title='Culinary Journeys', subtitle='TASTE THE WORLD', description='Embark on a gastronomic adventure through the world\'s finest kitchens.', image='https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=80', link='#'),
    ]

def _sample_funfacts():
    return [
        _S(title='The Wings Of Tatev', description='World\'s longest reversible aerial tramway at 5,752 meters.', emoji='🚡', image='https://images.unsplash.com/photo-1605649487212-47bdab064df7?w=600&q=80'),
        _S(title='Oldest Winery', description='The Armenian plateau is the birthplace of winemaking, 6,100 years old.', emoji='🍷', image='https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=600&q=80'),
        _S(title='Unique Alphabet', description='39 letters, one of the oldest scripts in the world, codified in 405 AD.', emoji='📜', image='https://images.unsplash.com/photo-1455390582262-044cdead277a?w=600&q=80'),
        _S(title='Older Than Rome', description='The capital Yerevan is over 2,800 years old — older than Rome!', emoji='🏛️', image='https://images.unsplash.com/photo-1567604130959-fc16b5a1c8cf?w=600&q=80'),
        _S(title='Ancient Footwear', description='The oldest leather shoe was discovered here — 5,500 years old.', emoji='👟', image='https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600&q=80'),
        _S(title='First Christian Nation', description='Armenia was the first nation to adopt Christianity in 301 AD.', emoji='⛪', image='https://images.unsplash.com/photo-1590012314607-cda9d9b699ae?w=600&q=80'),
    ]

def _sample_testimonials():
    return [
        _S(quote='Voyage transformed our honeymoon into something beyond our wildest dreams. Every detail was perfect.', author_name='Priya & Rahul Sharma', author_destination='Santorini, Greece', author_image=''),
        _S(quote='They don\'t just plan trips — they design experiences that stay with you forever.', author_name='Anita Desai', author_destination='Kyoto, Japan', author_image=''),
        _S(quote='The attention to detail was extraordinary. They anticipated our needs before we even knew them.', author_name='James & Sarah Mitchell', author_destination='Amalfi Coast, Italy', author_image=''),
    ]

def _sample_stats():
    return [
        _S(value=500, suffix='+', prefix='', label='Destinations'),
        _S(value=12, suffix='K+', prefix='', label='Happy Travelers'),
        _S(value=98, suffix='%', prefix='', label='Satisfaction'),
        _S(value=15, suffix='+', prefix='', label='Years Experience'),
    ]

def _sample_marquee():
    return [_S(word=w) for w in ['EXPLORE', '✦', 'DISCOVER', '✦', 'ADVENTURE', '✦', 'WANDER', '✦', 'DREAM', '✦', 'ESCAPE', '✦']]
