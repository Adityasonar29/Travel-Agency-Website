from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_replied = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.subject}"


class SiteSettings(models.Model):
    """Singleton model for global site settings."""
    site_name = models.CharField(max_length=100, default='VOYAGE')
    tagline = models.CharField(max_length=300, blank=True, default='Curated journeys that transform travel into art')
    hero_video = models.FileField(upload_to='videos/', blank=True)
    hero_heading_line1 = models.CharField(max_length=200, default='Beyond the')
    hero_heading_line2 = models.CharField(max_length=200, default='Horizon')
    hero_subtitle = models.TextField(blank=True, default='Curated journeys that transform travel into art')
    hero_cta_text = models.CharField(max_length=100, default='Begin Your Journey')
    about_overline = models.CharField(max_length=200, blank=True, default='MADE WITH PASSION')
    about_heading = models.CharField(max_length=200, blank=True, default='We Design Emotion')
    about_text = models.TextField(blank=True, default='We believe that travel is not about destinations — it is about feelings. Every journey we craft is a conversation between you and the world, shaped by curiosity, wonder, and the pursuit of something extraordinary.')
    about_image = models.ImageField(upload_to='about/', blank=True)
    email = models.EmailField(blank=True, default='hello@voyagetravel.com')
    phone = models.CharField(max_length=20, blank=True, default='+91 98765 43210')
    address = models.TextField(blank=True, default='Mumbai, Maharashtra, India')
    instagram = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    twitter = models.URLField(blank=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AboutPage(models.Model):
    """Singleton model for About page content."""

    # Hero
    hero_overline = models.CharField(
        max_length=200,
        default="OUR STORY"
    )

    hero_heading = models.CharField(
        max_length=250,
        default="Crafting Journeys That Shape Your Story"
    )

    hero_subheading = models.TextField(
        default="We create immersive travel experiences for curious explorers, combining thoughtful planning, local expertise, and unforgettable moments into every journey."
    )

    hero_image = models.ImageField(
        upload_to="about/",
        blank=True
    )

    # Story
    story_overline = models.CharField(
        max_length=200,
        default="HOW IT ALL STARTED"
    )

    story_heading = models.CharField(
        max_length=250,
        default="Born From a Passion for Meaningful Travel"
    )

    story_text = models.TextField(
        default="""
Voyage began with one simple belief — the best memories are created when travel feels personal.

What started as a shared passion for discovering hidden places slowly became a mission to help others experience the world with the same excitement. Instead of rushed schedules and crowded tourist attractions, we focus on carefully designed journeys that balance comfort, authenticity, and unforgettable moments.

Every destination we offer has been selected because it tells a story. Every itinerary is created to let travelers experience local culture, breathtaking landscapes, and genuine connections without worrying about complicated planning.

Today, Voyage continues to craft experiences that inspire curiosity, encourage exploration, and create memories that last long after the journey ends.
"""
    )

    story_image = models.ImageField(
        upload_to="about/",
        blank=True
    )

    vision_title = models.CharField(
        max_length=200,
        default="Redefining Exploration for the Conscious Traveler"
    )

    vision_text = models.TextField(
        default="Our goal is to transform global tourism by making deeply immersive, culturally respectful, and carbon-neutral journeys the gold standard for every adventurer"
    )

    mission_title = models.CharField(
        max_length=200,
        default="Connecting Cultures, Protecting Communities, and Elevating Journeys"
    )

    mission_text = models.TextField(
        default="Our mission is to engineer flawless, stress-free travel experiences and support local economies. ensuring you can immerse yourself fully and safely in the world’s most authentic destinations."
    )

    # Values
    values_heading = models.CharField(
        max_length=200,
        default="What We Believe"
    )

    value_one_title = models.CharField(
        max_length=100,
        default="Authentic Experiences"
    )

    value_one_text = models.TextField(
        default="Every itinerary is designed around genuine local culture rather than crowded tourist attractions."
    )

    value_two_title = models.CharField(
        max_length=100,
        default="Travel With Confidence"
    )

    value_two_text = models.TextField(
        default="Trusted partners, verified accommodations, and dedicated support from the beginning of your trip until you return home."
    )

    value_three_title = models.CharField(
        max_length=100,
        default="Thoughtfully Curated"
    )

    value_three_text = models.TextField(
        default="Every hotel, activity, and destination is chosen to create a seamless and memorable experience."
    )

    # Closing CTA
    cta_heading = models.CharField(
        max_length=250,
        default="Ready for Your Next Adventure?"
    )

    cta_text = models.TextField(
        default="Discover destinations that inspire curiosity and let us create a journey designed entirely around you."
    )

    cta_button = models.CharField(
        max_length=100,
        default="Explore Destinations"
    )

    class Meta:
        verbose_name = "About Page"
        verbose_name_plural = "About Page"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "About Page"

class Destination(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    hero_image = models.URLField(blank=True)
    image = models.ImageField(upload_to='destinations/')
    hover_image = models.ImageField(upload_to='destinations/hover/', blank=True)
    gallery = models.JSONField(blank=True, default=list)
    best_time_to_travel = models.CharField(max_length=100, blank=True)
    weather = models.CharField(max_length=200, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.8)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    nearby_places = models.JSONField(blank=True, default=list)
    reviews = models.JSONField(blank=True, default=list)
    related_tours_text = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name}, {self.country}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or 'destination'
            slug = base_slug
            counter = 1
            while Destination.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        slug = self.slug or slugify(self.name)
        return reverse('core:destination_detail', args=[slug])

class FunFact(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='funfacts/')
    emoji = models.CharField(max_length=10, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Tour(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    summary = models.CharField(max_length=255, blank=True)
    destinations = models.ManyToManyField('Destination', related_name='tours')
    duration = models.CharField(max_length=100, blank=True)
    duration_days = models.IntegerField(default=0)
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    budget_range = models.CharField(max_length=100, blank=True)
    transport_modes = models.JSONField(blank=True, default=list)
    hotels = models.JSONField(blank=True, default=list)
    meals = models.JSONField(blank=True, default=list)
    guides = models.JSONField(blank=True, default=list)
    seats_available = models.IntegerField(default=0)
    max_capacity = models.IntegerField(default=0)
    overview = models.TextField(blank=True)
    itinerary = models.JSONField(blank=True, default=list)
    included_items = models.JSONField(blank=True, default=list)
    excluded_items = models.JSONField(blank=True, default=list)
    gallery = models.JSONField(blank=True, default=list)
    reviews = models.JSONField(blank=True, default=list)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.8)
    hero_image = models.URLField(blank=True)
    image = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or 'tour'
            slug = base_slug
            counter = 1
            while Tour.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        slug = self.slug or slugify(self.name)
        return reverse('core:tour_detail', args=[slug])

    @property
    def is_available(self):
        return self.seats_available > 0




class Experience(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='experiences/')
    link = models.URLField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title




class Testimonial(models.Model):
    quote = models.TextField()
    author_name = models.CharField(max_length=200)
    author_destination = models.CharField(max_length=200)
    author_image = models.ImageField(upload_to='testimonials/', blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.author_name} — {self.author_destination}"


class Stat(models.Model):
    value = models.IntegerField()
    suffix = models.CharField(max_length=10, default='+')
    prefix = models.CharField(max_length=10, blank=True)
    label = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.prefix}{self.value}{self.suffix} — {self.label}"


class MarqueeWord(models.Model):
    word = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.CharField(max_length=200)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog_images/')
    status = models.CharField(max_length=10, choices=[('Draft', 'Draft'), ('Publish', 'Publish')], default='Draft')
    tags = models.CharField(max_length=200, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    related_tours = models.ManyToManyField('Tour', blank=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title


  # Change this path to match your Destination model location


