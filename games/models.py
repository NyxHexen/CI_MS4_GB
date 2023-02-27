from django.db import models
from django.utils.timezone import now

# Create your models here.

class Game(models.Model):
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254)
    genres = models.ManyToManyField('Genre')
    publishers = models.ForeignKey('Publisher', on_delete=models.CASCADE)
    developers = models.ManyToManyField('Developer')
    release_date = models.DateField(null=True)
    description = models.TextField(null=True)
    platforms = models.ManyToManyField('Platform', blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    media = models.ManyToManyField('Media', blank=True)
    base_price = models.DecimalField(max_digits=6, decimal_places=2)
    in_promo = models.BooleanField(default=False, null=True, blank=True)
    promo = models.ForeignKey('promo.Promo', null=True, blank=True, on_delete=models.SET_NULL)
    promo_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    promo_percentage = models.PositiveIntegerField(null=True, blank=True)
    final_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self) -> str:
        return self.slug

    def get_friendly_name(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.base_price != 0:
            self.final_price = self.base_price
        super().save(*args, **kwargs)


class DLC(models.Model):
    class Meta:
        verbose_name_plural = 'DLCs'

    required_game = models.ForeignKey('Game', default=None, on_delete=models.CASCADE)
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254)
    publishers = models.ForeignKey('Publisher', on_delete=models.CASCADE)
    developers = models.ManyToManyField('Developer')
    release_date = models.DateField(null=True)
    description = models.TextField(null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    media = models.ManyToManyField('Media', blank=True)

    def __str__(self) -> str:
        return self.slug

    def get_friendly_name(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=254)
    slug = models.SlugField()

    def __str__(self) -> str:
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=254)
    slug = models.SlugField()

    def __str__(self) -> str:
        return self.name

class Developer(models.Model):
    name = models.CharField(max_length=254)
    slug = models.SlugField()

    def __str__(self) -> str:
        return self.name


class RatingSet(models.Model):
    game = models.OneToOneField('Game', on_delete=models.CASCADE)
    esrb_ratings = models.ManyToManyField('EsrbRating')

    def __str__(self) -> str:
        return self.game.name


class EsrbRating(models.Model):
    name = models.CharField(max_length=254)
    slug = models.SlugField()

    def __str__(self) -> str:
        return self.name

    
class Platform(models.Model):
    name = models.CharField(max_length=254)
    slug = models.SlugField()

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=254)
    slug = models.SlugField()

    def __str__(self) -> str:
        return self.name


class Media(models.Model):
    class Meta:
        verbose_name_plural = 'Media'

    name = models.CharField(max_length=254, default='Untitled$')
    file = models.FileField(null=True, blank=True)
    media_url = models.URLField(max_length=1024, null=True, blank=True)
    media_type = models.CharField(max_length=6, null=True, blank=True)
    description = models.CharField(null=True, max_length=526)

    def __str__(self) -> str:
        return self.name
