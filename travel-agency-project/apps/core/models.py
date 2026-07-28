from django.db import models


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


class Destination(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='destinations/')
    hover_image = models.ImageField(upload_to='destinations/hover/', blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name}, {self.country}"


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

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.word
