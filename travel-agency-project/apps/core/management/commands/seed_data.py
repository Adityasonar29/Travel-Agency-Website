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
            ('Santorini', 'Greece', 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&q=80', 'https://images.unsplash.com/photo-1533105079780-92b9be482077?w=800&q=80'),
            ('Amalfi Coast', 'Italy', 'https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=800&q=80', 'https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=800&q=80'),
            ('Bali', 'Indonesia', 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&q=80', 'https://images.unsplash.com/photo-1518548419970-58e3b4079ab2?w=800&q=80'),
            ('Paris', 'France', 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80', 'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=800&q=80'),
            ('Kyoto', 'Japan', 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80', 'https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=800&q=80'),
            ('Tuscany', 'Italy', 'https://images.unsplash.com/photo-1516483638261-f4dbaf036963?w=800&q=80', 'https://images.unsplash.com/photo-1529260830199-42c24126f198?w=800&q=80'),
        ]
        for i, (name, country, img, hover) in enumerate(destinations):
            Destination.objects.get_or_create(name=name, defaults={
                'country': country, 'image': img, 'hover_image': hover, 'is_featured': True, 'order': i,
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
