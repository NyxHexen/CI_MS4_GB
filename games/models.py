from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
import os

# Create your models here.

class CustomBaseModel(models.Model):
    """
    DRY!
    """
    class Meta:
        abstract = True

    def model_name(self):
        return self._meta.model_name

    def __init__(self, *args, **kwargs):
        if "slug" in self.__dict__ and self.slug is None:
            self.slug = slugify(self.name)
        super().__init__(*args, **kwargs)
        

    def save(self, *args, **kwargs):
        if "slug" in self.__dict__ and self.slug is None:
            self.slug = slugify(self.name)
        if "base_price" in self.__dict__:
            if self.base_price != 0.00:
                self.final_price = self.base_price
        if "promo_percentage" in self.__dict__ and self.__dict__["promo_percentage"] != 0:
            self.__dict__["final_price"] = float(self.__dict__["base_price"]) * (1 + (self.__dict__["promo_percentage"] / 100 * -1 ))
        super().save(*args, **kwargs)


class Game(CustomBaseModel):
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, null=True, blank=True)
    genres = models.ManyToManyField('Genre')
    publisher = models.ForeignKey('Publisher', on_delete=models.CASCADE)
    developers = models.ManyToManyField('Developer')
    release_date = models.DateField(null=True)
    description = models.TextField(null=True)
    platforms = models.ManyToManyField('Platform', blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    media = models.ManyToManyField('Media', blank=True)
    featured = models.BooleanField(default=False, null=True, blank=True)
    carousel = models.BooleanField(default=False, null=True, blank=True)
    base_price = models.DecimalField(max_digits=6, decimal_places=2)
    in_promo = models.BooleanField(default=False, null=True, blank=True)
    promo = models.ForeignKey('promo.Promo', null=True, blank=True, on_delete=models.SET_NULL)
    promo_percentage = models.PositiveIntegerField(default=0, null=True, blank=True)
    final_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)


    def __str__(self) -> str:
        return self.slug

    def get_friendly_name(self):
        return self.name
    
    def promo_percentage_with_suffix(self):
        return f'{self.promo_percentage}%'
    
    def base_price_with_prefix(self):
        return f'£{self.base_price}'
    
    def final_price_with_prefix(self):
        return f'£{self.final_price}'

    promo_percentage_with_suffix.short_description = "Discount"
    base_price_with_prefix.short_description = "Base Price"
    final_price_with_prefix.short_description = "Final Price"


class DLC(CustomBaseModel):
    class Meta:
        verbose_name_plural = 'DLCs'

    required_game = models.ForeignKey('Game', default=None, on_delete=models.CASCADE)
    name = models.CharField(max_length=254, null=True, blank=True)
    slug = models.SlugField(max_length=254)
    publisher = models.ForeignKey('Publisher', on_delete=models.CASCADE)
    developers = models.ManyToManyField('Developer')
    release_date = models.DateField(null=True)
    description = models.TextField(null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    media = models.ManyToManyField('Media', blank=True)
    featured = models.BooleanField(default=False, null=True, blank=True)
    carousel = models.BooleanField(default=False, null=True, blank=True)
    base_price = models.DecimalField(max_digits=6, decimal_places=2)
    in_promo = models.BooleanField(default=False, null=True, blank=True)
    promo = models.ForeignKey('promo.Promo', null=True, blank=True, on_delete=models.SET_NULL)
    promo_percentage = models.PositiveIntegerField(default=0, null=True, blank=True)
    final_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self) -> str:
        return self.slug

    def get_friendly_name(self):
        return self.name
    
    def promo_percentage_with_suffix(self):
        return f'{self.promo_percentage}%'
    
    def base_price_with_prefix(self):
        return f'£{self.base_price}'
    
    def final_price_with_prefix(self):
        return f'£{self.final_price}'

    promo_percentage_with_suffix.short_description = "Discount"
    base_price_with_prefix.short_description = "Base Price"
    final_price_with_prefix.short_description = "Final Price"



class Genre(CustomBaseModel):
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, null=True, blank=True)
    game_list = models.Field

    def __str__(self) -> str:
        return self.name


class Publisher(CustomBaseModel):
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

class Developer(CustomBaseModel):
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class RatingSet(CustomBaseModel):
    game = models.OneToOneField('Game', on_delete=models.CASCADE)
    esrb_ratings = models.ManyToManyField('EsrbRating')

    def __str__(self) -> str:
        return self.game.name


class EsrbRating(CustomBaseModel):
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    
class Platform(CustomBaseModel):
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, null=True, blank=True)
    icon = models.ImageField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name
    

class Tag(CustomBaseModel):
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class Media(CustomBaseModel):
    class Meta:
        verbose_name_plural = 'Media'

    class MediaUseChoices(models.TextChoices):
        COVER = 'COVER', ('Cover Image')
        LANDING = 'LANDING', ('Landing Image')
        PREVIEW = 'PREVIEW', ('Preview Media')
        OTHER = 'OTHER', ('Other Media')

    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, null=True, blank=True)
    file = models.ImageField(null=True, blank=True)
    media_type = models.CharField(max_length=6, null=True,
                                  choices=[('image', 'Image'), ('video', 'Video')])
    media_use = models.CharField(max_length=24, default=MediaUseChoices.OTHER, choices=MediaUseChoices.choices)
    media_ext = models.CharField(max_length=6, null=True, blank=True)
    description = models.CharField(null=True, max_length=526)

    def __str__(self) -> str:
        return self.name


@receiver(pre_save, sender=Media)
def receiver(instance, *args, **kwargs):

    if instance.file._file is not None: # If a file is being uploaded
        _, new_file_extension = os.path.splitext(instance.file._file.name)
        new_file_extension = new_file_extension.replace('.', '')

    if len(instance.file.name) != 0:
        _, curr_file_extension = os.path.splitext(instance.file.name)
        curr_file_extension = curr_file_extension.replace('.', '')

    if  len(instance.file.name) != 0 and instance.media_ext is not None and instance.file._file is None:
        print("File exists, there is a media extension, and no new file is coming in.")
        if curr_file_extension != instance.media_ext:
            print("Auto-fill media extension.")
            instance.media_ext = curr_file_extension
    elif (instance.media_ext is None):
        print("There is no media extension.")
        if instance.file._file is not None:
            print(", but there is a new file coming in.")
            instance.media_ext = new_file_extension
        elif (len(instance.file.name) != 0):
            print(", but there's a file already.")
            instance.media_ext = curr_file_extension
    elif (instance.media_ext is not None and len(instance.file.name) == 0 ):
        print("There is no extension and no file.")
        instance.media_ext = None
    elif (instance.media_ext is not None and instance.file._file is not None):
        print("There is an extension, but a new file is coming in.")
        instance.media_ext = new_file_extension
    else: 
        print("None of the above applied.")
        print("If a cover photo exists already, don't save.")

