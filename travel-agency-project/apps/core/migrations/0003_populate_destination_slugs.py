from django.db import migrations
from django.utils.text import slugify


def generate_unique_slug(apps, schema_editor):
    Destination = apps.get_model('core', 'Destination')
    existing_slugs = set(Destination.objects.exclude(slug__isnull=True).values_list('slug', flat=True))

    for destination in Destination.objects.filter(slug__isnull=True):
        base_slug = slugify(destination.name) or 'destination'
        slug = base_slug
        counter = 1
        while slug in existing_slugs:
            slug = f"{base_slug}-{counter}"
            counter += 1
        destination.slug = slug
        existing_slugs.add(slug)
        destination.save(update_fields=['slug'])


def reverse_generate_unique_slug(apps, schema_editor):
    Destination = apps.get_model('core', 'Destination')
    Destination.objects.filter(slug__isnull=False).update(slug=None)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_destination_best_time_to_travel_destination_city_and_more'),
    ]

    operations = [
        migrations.RunPython(generate_unique_slug, reverse_generate_unique_slug),
    ]
