from django.shortcuts import render, get_object_or_404
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


def destination_detail(request, slug):
    destination = get_object_or_404(Destination, slug=slug)
    return render(request, 'pages/destination_detail.html', {
        'destination': destination,
        'show_loading': False,
    })


# ── Sample fallback data ──

class _S:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)
        if hasattr(self, 'name') and not hasattr(self, 'slug'):
            self.slug = self.name.lower().replace(' ', '-')

    def get_absolute_url(self):
        return f'/destinations/{self.slug}/'


def _sample_destinations():
    return [
        _S(
            name='Santorini',
            country='Greece',
            state='South Aegean',
            city='Oia',
            image='https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=1200&q=80',
            hover_image='https://images.unsplash.com/photo-1533105079780-92b9be482077?w=1200&q=80',
            hero_image='https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1400&q=80',
            description='Santorini is the jewel of the Aegean, known for whitewashed cliffside villages, cobalt-domed churches, and sunsets that paint the caldera in golden light.',
            gallery=[
                'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80',
                'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=800&q=80',
                'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&q=80',
            ],
            best_time_to_travel='April – October',
            weather='Warm Mediterranean sunshine with mild evenings',
            rating=4.9,
            latitude=36.3932,
            longitude=25.4615,
            nearby_places=[
                {'name': 'Fira Town', 'description': 'Vibrant cliffside capital with shopping, cafés and epic views.'},
                {'name': 'Akrotiri Ruins', 'description': 'Ancient Minoan site preserved beneath volcanic ash.'},
                {'name': 'Red Beach', 'description': 'Striking red-sand beach framed by dramatic black cliffs.'},
            ],
            reviews=[
                {'author': 'Mira Patel', 'date': 'March 2026', 'text': 'Santorini felt like a postcard come to life — the sunsets, villages and food were unforgettable.'},
                {'author': 'Noah Williams', 'date': 'June 2025', 'text': 'Perfect mix of romance and adventure. The caldera views were extraordinary.'},
            ],
            related_tours_text='Discover private yacht cruises, sunset caldera hikes, and boutique wine tastings designed to feel effortlessly luxurious.',
        ),
        _S(
            name='Amalfi Coast',
            country='Italy',
            state='Campania',
            city='Amalfi',
            image='https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=1200&q=80',
            hover_image='https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=1200&q=80',
            hero_image='https://images.unsplash.com/photo-1500534623283-312aade485b7?w=1400&q=80',
            description='The Amalfi Coast is a stunning Mediterranean corridor of pastel villages, lush lemon groves and cliffside roads with sweeping sea views.',
            gallery=[
                'https://images.unsplash.com/photo-1500534623283-312aade485b7?w=800&q=80',
                'https://images.unsplash.com/photo-1483721310020-03333e577078?w=800&q=80',
                'https://images.unsplash.com/photo-1505991401110-9edb43c668ec?w=800&q=80',
            ],
            best_time_to_travel='May – September',
            weather='Warm, sunny and ideal for seaside exploration',
            rating=4.8,
            latitude=40.6333,
            longitude=14.6020,
            nearby_places=[
                {'name': 'Positano', 'description': 'Iconic cliffside village with narrow streets and boutique shopping.'},
                {'name': 'Ravello Gardens', 'description': 'Historic terraces above the sea with sweeping coastal vistas.'},
                {'name': 'Path of the Gods', 'description': 'Scenic hiking route offering panoramic views of the Mediterranean.'},
            ],
            reviews=[
                {'author': 'Elena Rossi', 'date': 'May 2025', 'text': 'A magical coastline of color and charm. Every village felt like a hidden treasure.'},
                {'author': 'Daniel Kim', 'date': 'August 2024', 'text': 'Stunning scenery and the best seafood lunch I have ever had on Italy’s coast.'},
            ],
            related_tours_text='Enjoy pastel coastal road trips, Michelin dining experiences and private boat charters on this iconic shoreline.',
        ),
        _S(
            name='Bali',
            country='Indonesia',
            state='Bali Province',
            city='Ubud',
            image='https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=1200&q=80',
            hover_image='https://images.unsplash.com/photo-1518548419970-58e3b4079ab2?w=1200&q=80',
            hero_image='https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=1400&q=80',
            description='Bali blends lush rice terraces, volcanic peaks and vibrant temple culture for a soulful island escape full of discovery.',
            gallery=[
                'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=800&q=80',
                'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=800&q=80',
                'https://images.unsplash.com/photo-1493558103817-58b2924bce98?w=800&q=80',
            ],
            best_time_to_travel='April – October',
            weather='Warm tropical climate with dry, sunny days',
            rating=4.7,
            latitude=-8.3405,
            longitude=115.0920,
            nearby_places=[
                {'name': 'Ubud Monkey Forest', 'description': 'Sacred sanctuary inhabited by playful macaques.'},
                {'name': 'Tegallalang Rice Terraces', 'description': 'Iconic tiered rice fields enveloped in emerald green.'},
                {'name': 'Tanah Lot Temple', 'description': 'Dramatic sea temple perched on a rocky shoreline.'},
            ],
            reviews=[
                {'author': 'Sophie Lee', 'date': 'February 2026', 'text': 'Bali’s energy is unforgettable — from temple mornings to sunset beach clubs.'},
                {'author': 'Raj Malhotra', 'date': 'November 2025', 'text': 'The rice terraces and culture were the highlight of our Asian adventure.'},
            ],
            related_tours_text='Coming soon: guided temple rituals, jungle wellness retreats, and cultural discovery tours.',
        ),
        _S(
            name='Paris',
            country='France',
            state='Île-de-France',
            city='Paris',
            image='https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1200&q=80',
            hover_image='https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=1200&q=80',
            hero_image='https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=1400&q=80',
            description='Paris is the timeless city of art, cuisine and romance, where world-class museums meet charming boulevards and river views.',
            gallery=[
                'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&q=80',
                'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80',
                'https://images.unsplash.com/photo-1498598458177-6bdc35cb44d7?w=800&q=80',
            ],
            best_time_to_travel='April – June, September – October',
            weather='Mild spring and autumn days with crisp evenings',
            rating=4.9,
            latitude=48.8566,
            longitude=2.3522,
            nearby_places=[
                {'name': 'Eiffel Tower', 'description': 'Iconic landmark with panoramic city views.'},
                {'name': 'Louvre Museum', 'description': 'World-class museum home to the Mona Lisa.'},
                {'name': 'Montmartre', 'description': 'Historic hilltop neighborhood with artist studios and cafés.'},
            ],
            reviews=[
                {'author': 'Clara Bennett', 'date': 'June 2025', 'text': 'Paris felt magical at every turn — the museums, cafés, and riverwalk were absolute perfection.'},
                {'author': 'Ethan Brooks', 'date': 'April 2024', 'text': 'Timeless beauty and endless layers of style and history.'},
            ],
            related_tours_text='Luxury Seine cruises, private museum evenings and culinary walking itineraries are on the horizon.',
        ),
        _S(
            name='Kyoto',
            country='Japan',
            state='Kyoto Prefecture',
            city='Kyoto',
            image='https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=1200&q=80',
            hover_image='https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=1200&q=80',
            hero_image='https://images.unsplash.com/photo-1474452570157-3ad1f1202c17?w=1400&q=80',
            description='Kyoto blends ancient temples, bamboo forests and refined tradition in a city that feels like a living cultural museum.',
            gallery=[
                'https://images.unsplash.com/photo-1474452570157-3ad1f1202c17?w=800&q=80',
                'https://images.unsplash.com/photo-1503040689208-9e59ab6a5a3d?w=800&q=80',
                'https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=800&q=80',
            ],
            best_time_to_travel='March – May, October – November',
            weather='Comfortable spring blossoms and crisp autumn foliage',
            rating=4.8,
            latitude=35.0116,
            longitude=135.7681,
            nearby_places=[
                {'name': 'Fushimi Inari Shrine', 'description': 'Thousands of vermilion torii gates winding into the forest.'},
                {'name': 'Arashiyama Bamboo Grove', 'description': 'Peaceful bamboo forest paths with serene river views.'},
                {'name': 'Kinkaku-ji Temple', 'description': 'Golden pavilion shining above a reflective pond.'},
            ],
            reviews=[
                {'author': 'Yuki Tanaka', 'date': 'September 2025', 'text': 'Kyoto’s temples and gardens are among the most peaceful places I’ve ever visited.'},
                {'author': 'Hannah Smith', 'date': 'April 2024', 'text': 'Cherry blossoms and tea houses made Kyoto feel incredibly special.'},
            ],
            related_tours_text='Immersive temple tours, private tea ceremonies and seasonal foliage journeys are coming soon.',
        ),
        _S(
            name='Tuscany',
            country='Italy',
            state='Tuscany',
            city='Florence',
            image='https://images.unsplash.com/photo-1516483638261-f4dbaf036963?w=1200&q=80',
            hover_image='https://images.unsplash.com/photo-1529260830199-42c24126f198?w=1200&q=80',
            hero_image='https://images.unsplash.com/photo-1522098543979-ffc7f79d4c35?w=1400&q=80',
            description='Tuscany is a landscape of rolling hills, vineyards and hilltop towns where art, cuisine and countryside beauty come together.',
            gallery=[
                'https://images.unsplash.com/photo-1522098543979-ffc7f79d4c35?w=800&q=80',
                'https://images.unsplash.com/photo-1499825044458-518c9e533c09?w=800&q=80',
                'https://images.unsplash.com/photo-1500534623283-312aade485b7?w=800&q=80',
            ],
            best_time_to_travel='May – June, September – October',
            weather='Warm days and cool evenings with excellent vineyard light',
            rating=4.8,
            latitude=43.7711,
            longitude=11.2486,
            nearby_places=[
                {'name': 'Chianti Wine Region', 'description': 'Rolling vineyards with scenic tasting estates.'},
                {'name': 'Siena', 'description': 'Medieval city with sweeping piazzas and Gothic architecture.'},
                {'name': 'Pisa', 'description': 'Famous for its leaning tower and historic square.'},
            ],
            reviews=[
                {'author': 'Luca Bernini', 'date': 'July 2025', 'text': 'The light over Tuscany is unreal. Every road felt like a painting.'},
                {'author': 'Maya Jones', 'date': 'October 2024', 'text': 'Perfect countryside calm and Italian culinary excellence.'},
            ],
            related_tours_text='Related experiences will include vineyard escapes, truffle hunts and Renaissance art walks.',
        ),
    ]

def _sample_experiences():
    return [
        _S(title='Private Yacht Cruises', subtitle='LUXURY ON WATER', description='Sail through crystal-clear waters aboard a private yacht, with a personal crew catering to your every whim.', image='https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=1200&q=80', link='#'),
        _S(title='Mountain Retreats', subtitle='ELEVATED ESCAPES', description='Find solace in the mountains with curated retreats that blend adventure and tranquility.', image='https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1200&q=80', link='#'),
        _S(title='Culinary Journeys', subtitle='TASTE THE WORLD', description='Embark on a gastronomic adventure through the world\'s finest kitchens.', image='https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=80', link='#'),
    ]

def _sample_funfacts():
    return [
        _S(
            title='Visa-Free Adventure',
            description='Many travelers can visit Armenia visa-free or obtain an e-visa, making it an easy destination to explore.',
            emoji='🛂',
            image='https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=600&q=80'
        ),
        _S(
            title='Scenic Mountain Roads',
            description='Drive through breathtaking mountain passes, deep canyons, and picturesque villages across the country.',
            emoji='🏔️',
            image='https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=600&q=80'
        ),
        _S(
            title='UNESCO Heritage Sites',
            description='Visit magnificent monasteries and historic landmarks recognized as UNESCO World Heritage Sites.',
            emoji='🏛️',
            image='https://images.unsplash.com/photo-1516483638261-f4dbaf036963?w=600&q=80'
        ),
        _S(
            title='Year-Round Destination',
            description='Enjoy skiing in winter, hiking in summer, colorful autumn landscapes, and blooming spring valleys.',
            emoji='🌄',
            image='https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=600&q=80'
        ),
        _S(
            title='Lake Sevan Escape',
            description='Relax at one of the world’s largest high-altitude freshwater lakes with beaches, boating, and lakeside cafés.',
            emoji='🏞️',
            image='https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&q=80'
        ),
        _S(
            title='Local Food Experiences',
            description='Taste authentic Armenian cuisine, traditional barbecue, fresh lavash, and locally produced wines during your journey.',
            emoji='🍽️',
            image='https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=80'
        ),
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
