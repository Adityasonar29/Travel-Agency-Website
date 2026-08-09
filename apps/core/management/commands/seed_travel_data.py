import urllib.request
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.core.models import Destination, Tour, FunFact


IMAGE_HEADERS = {
    "User-Agent": "VOYAGE-Travel-Agency-Django-Seeder/1.0",
}

# Image mappings using free-to-use Unsplash URLs
DESTINATION_IMAGE_PAIRS = {
    "santorini": (
        "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=1600&q=85",
        "https://images.unsplash.com/photo-1533105079780-92b9be482077?w=1600&q=85",
    ),
    "amalfi-coast": (
        "https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=1600&q=85",
        "https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=1600&q=85",
    ),
    "bali": (
        "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=1600&q=85",
        "https://images.unsplash.com/photo-1518548419970-58e3b4079ab2?w=1600&q=85",
    ),
    "paris": (
        "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1600&q=85",
        "https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=1600&q=85",
    ),
    "kyoto": (
        "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=1600&q=85",
        "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=1600&q=85",
    ),
    "tuscany": (
        "https://images.unsplash.com/photo-1516483638261-f4dbaf036963?w=1600&q=85",
        "https://images.unsplash.com/photo-1529260830199-42c24126f198?w=1600&q=85",
    ),
    "dubai": (
        "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=1600&q=85",
        "https://images.unsplash.com/photo-1518684079-3c830dcef090?w=1600&q=85",
    ),
    "maldives": (
        "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=1600&q=85",
        "https://images.unsplash.com/photo-1573843981267-be1999ff37cd?w=1600&q=85",
    ),
    "swiss-alps": (
        "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=1600&q=85",
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1600&q=85",
    ),
    "iceland": (
        "https://images.unsplash.com/photo-1504829857797-ddff29c27927?w=1600&q=85",
        "https://images.unsplash.com/photo-1476610182048-b716b8518aae?w=1600&q=85",
    ),
}

FUNFACTS_DATA = [
    {
        "title": "Catacombs of Paris",
        "description": "Underneath the streets of Paris lie the remains of over 6 million people in a vast network of subterranean tunnels.",
        "emoji": "💀",
        "order": 1,
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80",
    },
    {
        "title": "Floating City of Venice",
        "description": "Venice is built on wooden logs driven into the waterlogged ground, imported from Croatia, Slovenia, and Montenegro centuries ago.",
        "emoji": "🛶",
        "order": 2,
        "image_url": "https://images.unsplash.com/photo-1514890547357-a9ee288728e0?w=800&q=80",
    },
    {
        "title": "Cappadocia's Underground World",
        "description": "Derinkuyu in Cappadocia is an ancient multi-level underground city that could accommodate up to 20,000 people.",
        "emoji": "🎈",
        "order": 3,
        "image_url": "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=800&q=80",
    },
]

DESTINATIONS = [
    {
        'name': 'Santorini',
        'country': 'Greece',
        'state': 'South Aegean',
        'city': 'Santorini',
        'hero_image': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=1800&q=90',
        'description': 'A cinematic Greek island of whitewashed villages, volcanic cliffs, blue-domed churches and golden-hour caldera views.',
        'best_time_to_travel': 'April–June, September–October',
        'weather': 'Mediterranean; warm, dry summers and mild winters.',
        'rating': Decimal('4.9'),
        'latitude': 36.3932,
        'longitude': 25.4615,
        'nearby_places': [
            {'name': 'Oia', 'type': 'Village', 'distance': '0 km'},
            {'name': 'Fira', 'type': 'Capital', 'distance': '11 km'},
            {'name': 'Red Beach', 'type': 'Beach', 'distance': '12 km'}
        ],
        'reviews': [
            {'name': 'Priya & Rahul', 'rating': 5, 'text': 'The caldera views were unreal and the whole trip felt beautifully paced.'},
            {'name': 'Maya S.', 'rating': 5, 'text': 'Perfect mix of village walks, food and quiet beach time.'}
        ],
        'related_tours_text': 'Pair Santorini with Athens and the Cyclades for a refined Greek escape.',
        'is_featured': True,
        'order': 1,
        'gallery': [
            'https://images.unsplash.com/photo-1500534623283-312aade485b7?w=1400&q=85',
            'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=1400&q=85'
        ]
    },
    {
        'name': 'Amalfi Coast',
        'country': 'Italy',
        'state': 'Campania',
        'city': 'Amalfi',
        'hero_image': 'https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=1800&q=90',
        'description': 'A dramatic Mediterranean coastline where pastel villages cling to cliffs above the Tyrrhenian Sea.',
        'best_time_to_travel': 'May–June, September–October',
        'weather': 'Mediterranean; sunny summers with mild coastal winters.',
        'rating': Decimal('4.9'),
        'latitude': 40.6333,
        'longitude': 14.6029,
        'nearby_places': [
            {'name': 'Positano', 'type': 'Coastal Town', 'distance': '19 km'},
            {'name': 'Ravello', 'type': 'Hill Town', 'distance': '7 km'}
        ],
        'reviews': [
            {'name': 'James M.', 'rating': 5, 'text': 'Every road looked like a postcard. The private boat day was the highlight.'}
        ],
        'related_tours_text': 'Combine the Amalfi Coast with Rome, Florence and Tuscany.',
        'is_featured': True,
        'order': 2,
        'gallery': [
            'https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=1400&q=85',
            'https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=1400&q=85'
        ]
    },
    {
        'name': 'Bali',
        'country': 'Indonesia',
        'state': 'Bali',
        'city': 'Ubud',
        'hero_image': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=1800&q=90',
        'description': 'A lush island where rice terraces, temple ceremonies, volcanic landscapes and warm beaches create an easy rhythm.',
        'best_time_to_travel': 'April–October',
        'weather': 'Tropical; warm year-round with a drier season from April to October.',
        'rating': Decimal('4.8'),
        'latitude': -8.4095,
        'longitude': 115.1889,
        'nearby_places': [
            {'name': 'Ubud', 'type': 'Cultural Hub', 'distance': '0 km'},
            {'name': 'Tegallalang Rice Terraces', 'type': 'Landscape', 'distance': '15 km'}
        ],
        'reviews': [
            {'name': 'Neha K.', 'rating': 5, 'text': 'The villa, temple visits and food experiences were perfectly balanced.'}
        ],
        'related_tours_text': 'Add Bali to a Southeast Asia itinerary with Singapore or combine Ubud and the coast.',
        'is_featured': True,
        'order': 3,
        'gallery': [
            'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=1400&q=85',
            'https://images.unsplash.com/photo-1518548419970-58e3b4079ab2?w=1400&q=85'
        ]
    }
]

TOURS = [
    {
        'name': 'Greek Isles — Blue Horizons',
        'summary': 'Santorini, Mykonos and Athens in one polished Mediterranean journey.',
        'destination_names': ['Santorini'],
        'duration': '8 Days / 7 Nights',
        'duration_days': 8,
        'price_per_person': Decimal('1499.00'),
        'budget_range': '₹1,25,000–₹1,60,000',
        'transport_modes': ['Private airport transfers', 'Ferry', 'Executive coach', 'Private boat'],
        'hotels': ['Caldera-view boutique hotel', 'Design hotel in Athens', 'Beachfront Mykonian stay'],
        'meals': ['7 breakfasts', '3 lunches', '2 curated dinners', 'Sunset mezze experience'],
        'guides': ['English-speaking local guides', 'Private Athens guide', 'Island host'],
        'seats_available': 12,
        'max_capacity': 18,
        'overview': 'A relaxed Greek escape designed around island views, local food and just enough structure to keep the journey effortless.',
        'itinerary': [
            {'day': 1, 'title': 'Arrive in Athens', 'description': 'Private transfer, hotel check-in and a relaxed evening in Plaka.'},
            {'day': 2, 'title': 'Athens in Context', 'description': 'Guided Acropolis visit followed by a food-focused afternoon.'},
            {'day': 3, 'title': 'Sail to Santorini', 'description': 'Fast ferry to Santorini and sunset check-in overlooking the caldera.'}
        ],
        'included_items': ['Boutique accommodation', 'Daily breakfast', 'Private transfers', 'Ferry tickets', 'Catamaran cruise'],
        'excluded_items': ['International flights', 'Travel insurance', 'Personal shopping'],
        'gallery': [
            'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=1400&q=85',
            'https://images.unsplash.com/photo-1533105079780-92b9be482077?w=1400&q=85'
        ],
        'reviews': [
            {'name': 'Priya S.', 'rating': 5, 'text': 'Beautifully paced and incredibly easy from start to finish.'}
        ],
        'rating': Decimal('4.9'),
        'hero_image': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=1800&q=90',
        'image': 'https://images.unsplash.com/photo-1533105079780-92b9be482077?w=1200&q=85',
        'is_featured': True,
        'order': 1
    },
    {
        'name': 'Italian Grandeur — Rome to Amalfi',
        'summary': 'Art, food, Renaissance cities and the Mediterranean coast.',
        'destination_names': ['Amalfi Coast'],
        'duration': '10 Days / 9 Nights',
        'duration_days': 10,
        'price_per_person': Decimal('1899.00'),
        'budget_range': '₹1,55,000–₹2,05,000',
        'transport_modes': ['High-speed train', 'Private sedan', 'Ferry', 'Airport transfer'],
        'hotels': ['Historic Rome hotel', 'Tuscan vineyard stay', 'Amalfi boutique hotel'],
        'meals': ['9 breakfasts', '3 lunches', '3 dinners', 'Wine tasting'],
        'guides': ['Private art historian', 'Local food guide', 'Coastal guide'],
        'seats_available': 10,
        'max_capacity': 16,
        'overview': 'A cinematic route through Italy that moves from ancient Rome to Renaissance Florence and the cliffside villages of Amalfi.',
        'itinerary': [
            {'day': 1, 'title': 'Rome Arrival', 'description': 'Private transfer and evening aperitivo.'},
            {'day': 2, 'title': 'Ancient Rome', 'description': 'Colosseum and Roman Forum with a private historian.'}
        ],
        'included_items': ['9 nights accommodation', 'Breakfast daily', 'Private transfers', 'Train tickets'],
        'excluded_items': ['International flights', 'Insurance', 'Personal expenses'],
        'gallery': [
            'https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=1400&q=85',
            'https://images.unsplash.com/photo-1516483638261-f4dbaf036963?w=1400&q=85'
        ],
        'reviews': [
            {'name': 'James M.', 'rating': 5, 'text': 'The itinerary had all the classics without feeling rushed.'}
        ],
        'rating': Decimal('4.9'),
        'hero_image': 'https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=1800&q=90',
        'image': 'https://images.unsplash.com/photo-1516483638261-f4dbaf036963?w=1200&q=85', 'is_featured': True,
        'order': 2
    },
    {
        'name': 'Bali Slow Escape',
        'summary': 'Rice terraces, temples, rainforest and beach days without the rush.',
        'destination_names': ['Bali'],
        'duration': '7 Days / 6 Nights',
        'duration_days': 7,
        'price_per_person': Decimal('999.00'),
        'budget_range': '₹82,000–₹1,10,000',
        'transport_modes': ['Private car', 'Fast boat', 'Airport transfer'],
        'hotels': ['Ubud jungle retreat', 'Uluwatu cliffside resort'],
        'meals': ['6 breakfasts', '2 lunches', '2 dinners', 'Balinese cooking class'],
        'guides': ['Local cultural guide', 'Nature guide', 'Wellness host'],
        'seats_available': 14,
        'max_capacity': 20,
        'overview': 'A balanced Bali itinerary with culture in Ubud, a sunrise volcano option, a cooking experience and coastal downtime.',
        'itinerary': [
            {'day': 1, 'title': 'Ubud Arrival', 'description': 'Private transfer, check-in and rice-field sunset walk.'},
            {'day': 2, 'title': 'Temples & Terraces', 'description': 'Tegallalang, Tirta Empul and a local lunch.'}
        ],
        'included_items': ['6 nights stay', 'Daily breakfast', 'Private vehicle', 'Temple visits', 'Cooking class'],
        'excluded_items': ['Flights', 'Travel insurance', 'Optional Mount Batur hike'],
        'gallery': [
            'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=1400&q=85',
            'https://images.unsplash.com/photo-1518548419970-58e3b4079ab2?w=1400&q=85'
        ],
        'reviews': [
            {'name': 'Neha K.', 'rating': 5, 'text': 'The balance between temples and beach time was perfect.'}
        ],
        'rating': Decimal('4.8'),
        'hero_image': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=1800&q=90',
        'image': 'https://images.unsplash.com/photo-1518548419970-58e3b4079ab2?w=1200&q=85',
        'is_featured': True,
        'order': 3
    }
]


def fetch_remote_image(url):
    """Utility function to safely fetch image data from an online URL."""
    try:
        req = urllib.request.Request(url, headers=IMAGE_HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read()
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return None


class Command(BaseCommand):
    help = "Seeds database with full travel destinations, tours, and fun facts using direct online URL imagery."

    def add_arguments(self, parser):
        parser.add_argument(
            '--download-images',
            action='store_true',
            help='Download online images into Django ImageFields locally instead of attaching remote links.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        download_images = options['download_images']
        self.stdout.write(self.style.MIGRATE_HEADING("Seeding VOYAGE travel data..."))

        # 1. Seed Fun Facts
        for fact_data in FUNFACTS_DATA:
            image_url = fact_data.pop("image_url", None)
            fact, created = FunFact.objects.update_or_create(
                title=fact_data["title"],
                defaults=fact_data
            )
            if image_url and download_images:
                img_data = fetch_remote_image(image_url)
                if img_data:
                    fact.image.save(f"{slugify(fact.title)}.jpg", ContentFile(img_data), save=True)
            elif image_url:
                fact.image = image_url
                fact.save()

            self.stdout.write(f"Synced FunFact: {fact.title}")

        # 2. Seed Destinations
        dest_map = {}
        for dest_data in DESTINATIONS:
            name = dest_data["name"]
            slug_key = slugify(name)

            dest, created = Destination.objects.update_or_create(
                name=name,
                defaults=dest_data
            )
            dest_map[name] = dest

            # Attach primary/hover images from online URL sources
            if slug_key in DESTINATION_IMAGE_PAIRS:
                main_url, hover_url = DESTINATION_IMAGE_PAIRS[slug_key]

                if download_images:
                    main_img_data = fetch_remote_image(main_url)
                    if main_img_data:
                        dest.image.save(f"{slug_key}.jpg", ContentFile(main_img_data), save=False)

                    hover_img_data = fetch_remote_image(hover_url)
                    if hover_img_data:
                        dest.hover_image.save(f"{slug_key}-hover.jpg", ContentFile(hover_img_data), save=False)
                else:
                    dest.image = main_url
                    dest.hover_image = hover_url

                dest.save()

            self.stdout.write(f"Synced Destination: {dest.name}")

        # 3. Seed Tours
        for tour_data in TOURS:
            dest_names = tour_data.pop("destination_names", [])
            tour, created = Tour.objects.update_or_create(
                name=tour_data["name"],
                defaults=tour_data
            )

            # Link destinations many-to-many relationship
            matched_dests = [dest_map[dname] for dname in dest_names if dname in dest_map]
            tour.destinations.set(matched_dests)

            self.stdout.write(f"Synced Tour: {tour.name}")

        self.stdout.write(self.style.SUCCESS("Successfully seeded all travel data!"))