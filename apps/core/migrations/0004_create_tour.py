from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_populate_destination_slugs'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tour',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=200, null=True, unique=True)),
                ('summary', models.CharField(blank=True, max_length=255)),
                ('duration', models.CharField(blank=True, max_length=100)),
                ('duration_days', models.IntegerField(default=0)),
                ('price_per_person', models.DecimalField(decimal_places=2, max_digits=10)),
                ('budget_range', models.CharField(blank=True, max_length=100)),
                ('transport_modes', models.JSONField(blank=True, default=list)),
                ('hotels', models.JSONField(blank=True, default=list)),
                ('meals', models.JSONField(blank=True, default=list)),
                ('guides', models.JSONField(blank=True, default=list)),
                ('seats_available', models.IntegerField(default=0)),
                ('max_capacity', models.IntegerField(default=0)),
                ('overview', models.TextField(blank=True)),
                ('itinerary', models.JSONField(blank=True, default=list)),
                ('included_items', models.JSONField(blank=True, default=list)),
                ('excluded_items', models.JSONField(blank=True, default=list)),
                ('gallery', models.JSONField(blank=True, default=list)),
                ('reviews', models.JSONField(blank=True, default=list)),
                ('rating', models.DecimalField(decimal_places=1, default=4.8, max_digits=3)),
                ('hero_image', models.URLField(blank=True)),
                ('image', models.URLField(blank=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=0)),
                ('destinations', models.ManyToManyField(related_name='tours', to='core.Destination')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
