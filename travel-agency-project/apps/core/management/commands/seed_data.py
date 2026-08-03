from django.core.management.base import BaseCommand
from apps.core.models import Destination, Experience, FunFact, Testimonial, Stat, MarqueeWord, SiteSettings


class Command(BaseCommand):
    help = 'Seed the database with sample travel data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Site Settings
        SiteSettings.objects.get_or_create(pk=1, defaults={
            'site_name': 'VOYAGE',
            'tagline': 'Curated journeys that transform travel into art',
            'hero_heading_line1': 'Beyond the',
            'hero_heading_line2': 'Horizon',
            'hero_subtitle': 'We design journeys that mirror your curiosity, your rhythm, and your pursuit of something extraordinary.',
            'hero_cta_text': 'Begin Your Journey',
            'about_overline': 'MADE WITH PASSION',
            'about_heading': 'We Design Emotion',
            'about_text': 'We believe that travel is not about destinations — it is about feelings. Every journey we craft is a conversation between you and the world, shaped by curiosity, wonder, and the pursuit of something extraordinary.',
            'email': 'hello@voyagetravel.com',
            'phone': '+91 98765 43210',
            'address': 'Mumbai, Maharashtra, India',
        })

        # Destinations
        destinations = [
            {
                'name': 'Santorini',
                'country': 'Greece',
                'state': 'South Aegean',
                'city': 'Oia',
                'image': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=1200&q=80',
                'hover_image': 'https://images.unsplash.com/photo-1533105079780-92b9be482077?w=1200&q=80',
                'hero_image': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1400&q=80',
                'description': 'Santorini is the jewel of the Aegean, famous for its whitewashed cliffside villages, cobalt-blue domes, and epic sunset views over the caldera.',
                'gallery': [
                    'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80',
                    'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=800&q=80',
                    'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&q=80',
                ],
                'best_time_to_travel': 'April – October',
                'weather': 'Warm Mediterranean sunshine, mild evenings',
                'rating': 4.9,
                'latitude': 36.3932,
                'longitude': 25.4615,
                'nearby_places': [
                    {'name': 'Fira Town', 'description': 'The island capital with lively markets, museums and cliff-edge views.'},
                    {'name': 'Akrotiri Ruins', 'description': 'Ancient Minoan settlement preserved under volcanic ash.'},
                    {'name': 'Red Beach', 'description': 'Striking red volcanic sand beach with dramatic cliffs.'},
                ],
                'reviews': [
                    {'author': 'Mira Patel', 'date': 'March 2026', 'text': 'Santorini felt like a postcard come to life — the sunsets, the villages, the food were all unforgettable.'},
                    {'author': 'Noah Williams', 'date': 'June 2025', 'text': 'Perfect mix of romance and adventure. The views from the cliffside restaurants were extraordinary.'},
                ],
                'related_tours_text': 'Coastal private yacht cruises, sunset caldera hikes, and boutique wine tours will be available soon.',
            },
            {
                'name': 'Amalfi Coast',
                'country': 'Italy',
                'state': 'Campania',
                'city': 'Amalfi',
                'image': 'https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=1200&q=80',
                'hover_image': 'https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=1200&q=80',
                'hero_image': 'https://images.unsplash.com/photo-1500534623283-312aade485b7?w=1400&q=80',
                'description': 'The Amalfi Coast is a dramatic coastline of pastel villages, lemon groves, and cliffside roads overlooking the Tyrrhenian Sea.',
                'gallery': [
                    'https://images.unsplash.com/photo-1500534623283-312aade485b7?w=800&q=80',
                    'https://images.unsplash.com/photo-1483721310020-03333e577078?w=800&q=80',
                    'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80',
                ],
                'best_time_to_travel': 'May – September',
                'weather': 'Sunny, warm and ideal for seaside exploration',
                'rating': 4.8,
                'latitude': 40.6333,
                'longitude': 14.6020,
                'nearby_places': [
                    {'name': 'Positano', 'description': 'Iconic cliffside village with narrow streets and boutique shops.'},
                    {'name': 'Ravello Gardens', 'description': 'Historic gardens with breathtaking terraces above the coast.'},
                    {'name': 'Path of the Gods', 'description': 'A scenic hiking route with panoramic Mediterranean views.'},
                ],
                'reviews': [
                    {'author': 'Elena Rossi', 'date': 'May 2025', 'text': 'A magical coastline of color and charm. Every village felt like a hidden treasure.'},
                    {'author': 'Daniel Kim', 'date': 'August 2024', 'text': 'Stunning scenery and the best seafood lunch I have ever had on Italy’s coast.'},
                ],
                'related_tours_text': 'Soon: pastel coastal road trips, Michelin dining experiences, and private boat charters.',
            },
            {
                'name': 'Bali',
                'country': 'Indonesia',
                'state': 'Bali Province',
                'city': 'Ubud',
                'image': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=1200&q=80',
                'hover_image': 'https://images.unsplash.com/photo-1518548419970-58e3b4079ab2?w=1200&q=80',
                'hero_image': 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=1400&q=80',
                'description': 'Bali blends lush rice terraces, volcanic peaks, vibrant temples, and a soulful culture that feels both wild and welcoming.',
                'gallery': [
                    'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=800&q=80',
                    'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=800&q=80',
                    'https://images.unsplash.com/photo-1493558103817-58b2924bce98?w=800&q=80',
                ],
                'best_time_to_travel': 'April – October',
                'weather': 'Warm tropical climate with dry, sunny days',
                'rating': 4.7,
                'latitude': -8.3405,
                'longitude': 115.0920,
                'nearby_places': [
                    {'name': 'Ubud Monkey Forest', 'description': 'Sacred sanctuary inhabited by playful macaques.'},
                    {'name': 'Tegallalang Rice Terraces', 'description': 'Iconic carved terraces with a serene, emerald landscape.'},
                    {'name': 'Tanah Lot Temple', 'description': 'Sea temple perched on a dramatic offshore rock.'},
                ],
                'reviews': [
                    {'author': 'Sophie Lee', 'date': 'February 2026', 'text': 'Bali’s energy is unforgettable — from temple mornings to sunset beach clubs.'},
                    {'author': 'Raj Malhotra', 'date': 'November 2025', 'text': 'The rice terraces and culture were the highlight of our Asian journey.'},
                ],
                'related_tours_text': 'Coming soon: guided temple rituals, jungle wellness retreats, and cultural discovery tours.',
            },
            {
                'name': 'Paris',
                'country': 'France',
                'state': 'Île-de-France',
                'city': 'Paris',
                'image': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1200&q=80',
                'hover_image': 'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=1200&q=80',
                'hero_image': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=1400&q=80',
                'description': 'Paris is the timeless city of art, cuisine, and romance, where world-class museums meet charming boulevards and river views.',
                'gallery': [
                    'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&q=80',
                    'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80',
                    'https://images.unsplash.com/photo-1498598458177-6bdc35cb44d7?w=800&q=80',
                ],
                'best_time_to_travel': 'April – June, September – October',
                'weather': 'Mild spring and autumn days with crisp evenings',
                'rating': 4.9,
                'latitude': 48.8566,
                'longitude': 2.3522,
                'nearby_places': [
                    {'name': 'Eiffel Tower', 'description': 'Iconic landmark with city-spanning views from the summit.'},
                    {'name': 'Louvre Museum', 'description': 'Home to world-famous art, including the Mona Lisa.'},
                    {'name': 'Montmartre', 'description': 'Historic hilltop neighborhood with winding streets and artists.’'},
                ],
                'reviews': [
                    {'author': 'Clara Bennett', 'date': 'June 2025', 'text': 'Paris felt magical at every turn — the museums, cafés, and riverwalks were absolute perfection.'},
                    {'author': 'Ethan Brooks', 'date': 'April 2024', 'text': 'Timeless city beauty with endless layers of style and history.'},
                ],
                'related_tours_text': 'Remaining tours will include luxury Seine cruises, private museum experiences, and culinary walking itineraries.',
            },
            {
                'name': 'Kyoto',
                'country': 'Japan',
                'state': 'Kyoto Prefecture',
                'city': 'Kyoto',
                'image': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=1200&q=80',
                'hover_image': 'https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=1200&q=80',
                'hero_image': 'https://images.unsplash.com/photo-1474452570157-3ad1f1202c17?w=1400&q=80',
                'description': 'Kyoto blends ancient temples, bamboo forests, and refined tradition in a city that feels like a living cultural museum.',
                'gallery': [
                    'https://images.unsplash.com/photo-1474452570157-3ad1f1202c17?w=800&q=80',
                    'https://images.unsplash.com/photo-1503040689208-9e59ab6a5a3d?w=800&q=80',
                    'https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=800&q=80',
                ],
                'best_time_to_travel': 'March – May, October – November',
                'weather': 'Comfortable spring blossoms and crisp autumn foliage',
                'rating': 4.8,
                'latitude': 35.0116,
                'longitude': 135.7681,
                'nearby_places': [
                    {'name': 'Fushimi Inari Shrine', 'description': 'Thousands of vermilion torii gates winding up the mountain.'},
                    {'name': 'Arashiyama Bamboo Grove', 'description': 'Peaceful bamboo forest paths with serene river views.'},
                    {'name': 'Kinkaku-ji Temple', 'description': 'Golden pavilion reflected in a tranquil pond.'},
                ],
                'reviews': [
                    {'author': 'Yuki Tanaka', 'date': 'September 2025', 'text': 'Kyoto’s temples and gardens are among the most peaceful places I’ve ever visited.'},
                    {'author': 'Hannah Smith', 'date': 'April 2024', 'text': 'Cherry blossoms and traditional tea houses made Kyoto feel utterly special.'},
                ],
                'related_tours_text': 'Future offerings include immersive temple tours, private tea ceremonies, and seasonal foliage journeys.',
            },
            {
                'name': 'Tuscany',
                'country': 'Italy',
                'state': 'Tuscany',
                'city': 'Florence',
                'image': 'https://images.unsplash.com/photo-1516483638261-f4dbaf036963?w=1200&q=80',
                'hover_image': 'https://images.unsplash.com/photo-1529260830199-42c24126f198?w=1200&q=80',
                'hero_image': 'https://images.unsplash.com/photo-1522098543979-ffc7f79d4c35?w=1400&q=80',
                'description': 'Tuscany is a landscape of rolling hills, vineyards, and hilltop towns where art, architecture and cuisine come together beautifully.',
                'gallery': [
                    'https://images.unsplash.com/photo-1522098543979-ffc7f79d4c35?w=800&q=80',
                    'https://images.unsplash.com/photo-1499825044458-518c9e533c09?w=800&q=80',
                    'https://images.unsplash.com/photo-1500534623283-312aade485b7?w=800&q=80',
                ],
                'best_time_to_travel': 'May – June, September – October',
                'weather': 'Warm days and cool evenings with excellent vineyard light',
                'rating': 4.8,
                'latitude': 43.7711,
                'longitude': 11.2486,
                'nearby_places': [
                    {'name': 'Chianti Wine Region', 'description': 'Rolling vineyards with scenic tasting estates and rustic villages.'},
                    {'name': 'Siena', 'description': 'Medieval city with sweeping piazzas and Gothic architecture.'},
                    {'name': 'Pisa', 'description': 'Famous for its leaning tower and historic square.'},
                ],
                'reviews': [
                    {'author': 'Luca Bernini', 'date': 'July 2025', 'text': 'The light over Tuscany is unreal. Every road felt like a painting.'},
                    {'author': 'Maya Jones', 'date': 'October 2024', 'text': 'Perfect mix of countryside calm and Italian culinary excellence.'},
                ],
                'related_tours_text': 'Related experiences will include vineyard escapes, truffle hunts, and Renaissance art walks.',
            },
        ]
        for i, dest in enumerate(destinations):
            Destination.objects.update_or_create(name=dest['name'], defaults={
                'country': dest['country'],
                'state': dest['state'],
                'city': dest['city'],
                'description': dest['description'],
                'hero_image': dest['hero_image'],
                'image': dest['image'],
                'hover_image': dest['hover_image'],
                'gallery': dest['gallery'],
                'best_time_to_travel': dest['best_time_to_travel'],
                'weather': dest['weather'],
                'rating': dest['rating'],
                'latitude': dest['latitude'],
                'longitude': dest['longitude'],
                'nearby_places': dest['nearby_places'],
                'reviews': dest['reviews'],
                'related_tours_text': dest['related_tours_text'],
                'is_featured': True,
                'order': i,
            })

        # Experiences
        experiences = [
            ('Private Yacht Cruises', 'LUXURY ON WATER', 'Sail through crystal-clear waters aboard a private yacht, with a personal crew catering to your every whim.', 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=1200&q=80'),
            ('Mountain Retreats', 'ELEVATED ESCAPES', 'Find solace in the mountains with curated retreats that blend adventure and tranquility.', 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1200&q=80'),
            ('Culinary Journeys', 'TASTE THE WORLD', 'Embark on a gastronomic adventure through the world\'s finest kitchens.', 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=80'),
        ]
        for i, (title, sub, desc, img) in enumerate(experiences):
            Experience.objects.get_or_create(title=title, defaults={
                'subtitle': sub, 'description': desc, 'image': img, 'order': i,
            })

        # Fun Facts
        funfacts = [
            ('The Wings Of Tatev', 'World\'s longest reversible aerial tramway at 5,752 meters.', '🚡', 'https://images.unsplash.com/photo-1605649487212-47bdab064df7?w=600&q=80'),
            ('Oldest Winery', 'The Armenian plateau is the birthplace of winemaking, 6,100 years old.', '🍷', 'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=600&q=80'),
            ('Unique Alphabet', '39 letters, one of the oldest scripts in the world, codified in 405 AD.', '📜', 'https://images.unsplash.com/photo-1455390582262-044cdead277a?w=600&q=80'),
            ('Older Than Rome', 'The capital Yerevan is over 2,800 years old — older than Rome!', '🏛️', 'https://images.unsplash.com/photo-1567604130959-fc16b5a1c8cf?w=600&q=80'),
            ('Ancient Footwear', 'The oldest leather shoe was discovered here — 5,500 years old.', '👟', 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600&q=80'),
            ('First Christian Nation', 'Armenia was the first nation to adopt Christianity in 301 AD.', '⛪', 'https://images.unsplash.com/photo-1590012314607-cda9d9b699ae?w=600&q=80'),
        ]
        for i, (title, desc, emoji, img) in enumerate(funfacts):
            FunFact.objects.get_or_create(title=title, defaults={
                'description': desc, 'emoji': emoji, 'image': img, 'order': i,
            })

        # Testimonials
        testimonials = [
            ('Voyage transformed our honeymoon into something beyond our wildest dreams. Every detail was perfect.', 'Priya & Rahul Sharma', 'Santorini, Greece'),
            ('They don\'t just plan trips — they design experiences that stay with you forever.', 'Anita Desai', 'Kyoto, Japan'),
            ('The attention to detail was extraordinary. They anticipated our needs before we even knew them.', 'James & Sarah Mitchell', 'Amalfi Coast, Italy'),
        ]
        for i, (quote, name, dest) in enumerate(testimonials):
            Testimonial.objects.get_or_create(author_name=name, defaults={
                'quote': quote, 'author_destination': dest, 'order': i,
            })

        # Stats
        stats = [
            (500, '+', '', 'Destinations'),
            (12, 'K+', '', 'Happy Travelers'),
            (98, '%', '', 'Satisfaction'),
            (15, '+', '', 'Years Experience'),
        ]
        for i, (val, suffix, prefix, label) in enumerate(stats):
            Stat.objects.get_or_create(label=label, defaults={
                'value': val, 'suffix': suffix, 'prefix': prefix, 'order': i,
            })

        # Marquee Words
        words = ['EXPLORE', '✦', 'DISCOVER', '✦', 'ADVENTURE', '✦', 'WANDER', '✦', 'DREAM', '✦', 'ESCAPE', '✦', 'VOYAGE', '✦', 'JOURNEY', '✦']
        for i, word in enumerate(words):
            MarqueeWord.objects.get_or_create(word=word, defaults={'order': i})

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
