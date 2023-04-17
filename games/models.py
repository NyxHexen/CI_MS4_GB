from django.db import models
from django.utils.text import slugify
from django.db.models import Avg
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from django_countries.fields import CountryField

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
        if "final_price" in self.__dict__ and self.final_price == 0:
            self.final_price = self.base_price
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        if "slug" in self.__dict__ and self.slug is None:
            self.slug = slugify(self.name)
        if (
            "final_price" in self.__dict__
            and self.final_price == 0
            and self.promo is None
        ):
            self.final_price = self.base_price
        super().save(*args, **kwargs)


class Game(CustomBaseModel):
    name = models.CharField(max_length=254, unique=True)
    slug = models.SlugField(max_length=254, unique=True, null=True, blank=True)
    description = models.TextField(default='', max_length=1024)
    storyline = models.TextField(default='', max_length=1024)
    genres = models.ManyToManyField("Genre")
    publishers = models.ManyToManyField("Publisher")
    developers = models.ManyToManyField("Developer")
    release_date = models.DateField(null=True)
    description = models.TextField(null=True)
    platforms = models.ManyToManyField("Platform")
    tags = models.ManyToManyField("Tag")
    features = models.ManyToManyField("Feature")
    media = models.ManyToManyField("Media")
    is_featured = models.BooleanField(default=False, null=True, blank=True)
    carousel = models.BooleanField(default=False, null=True, blank=True)
    base_price = models.DecimalField(max_digits=6, decimal_places=2)
    in_promo = models.BooleanField(default=False, null=True, blank=True)
    promo = models.ForeignKey(
        "promo.Promo", null=True, blank=True, on_delete=models.SET_NULL
    )
    promo_percentage = models.PositiveIntegerField(default=0, null=True, blank=True)
    final_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self) -> str:
        return self.name

    def promo_percentage_with_suffix(self):
        return f"{self.promo_percentage}%"

    def base_price_with_prefix(self):
        return f"£{self.base_price}"

    def final_price_with_prefix(self):
        return f"£{self.final_price}"

    promo_percentage_with_suffix.short_description = "Discount"
    base_price_with_prefix.short_description = "Base Price"
    final_price_with_prefix.short_description = "Final Price"


class DLC(CustomBaseModel):
    class Meta:
        verbose_name_plural = "DLCs"

    required_game = models.ForeignKey("Game", default=None, on_delete=models.CASCADE)
    name = models.CharField(max_length=254, unique=True)
    slug = models.SlugField(max_length=254, unique=True, null=True, blank=True)
    description = models.TextField(default='', max_length=1024)
    storyline = models.TextField(default='', max_length=1024)
    genres = models.ManyToManyField("Genre")
    publishers = models.ManyToManyField("Publisher")
    developers = models.ManyToManyField("Developer")
    release_date = models.DateField(null=True)
    description = models.TextField(null=True)
    platforms = models.ManyToManyField("Platform")
    tags = models.ManyToManyField("Tag")
    features = models.ManyToManyField("Feature")
    media = models.ManyToManyField("Media")
    is_featured = models.BooleanField(default=False, null=True, blank=True)
    carousel = models.BooleanField(default=False, null=True, blank=True)
    base_price = models.DecimalField(max_digits=6, decimal_places=2)
    in_promo = models.BooleanField(default=False, null=True, blank=True)
    promo = models.ForeignKey(
        "promo.Promo", null=True, blank=True, on_delete=models.SET_NULL
    )
    promo_percentage = models.PositiveIntegerField(default=0, null=True, blank=True)
    final_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)


    def __str__(self) -> str:
        return self.name

    def promo_percentage_with_suffix(self):
        return f"{self.promo_percentage}%"

    def base_price_with_prefix(self):
        return f"£{self.base_price}"

    def final_price_with_prefix(self):
        return f"£{self.final_price}"

    promo_percentage_with_suffix.short_description = "Discount"
    base_price_with_prefix.short_description = "Base Price"
    final_price_with_prefix.short_description = "Final Price"


class Genre(CustomBaseModel):
    name = models.CharField(max_length=254, unique=True)
    slug = models.SlugField(max_length=254, unique=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class Publisher(CustomBaseModel):
    name = models.CharField(max_length=254, unique=True)
    slug = models.SlugField(max_length=254, unique=True, null=True, blank=True)
    description = models.CharField(max_length=500, default='')
    official_site = models.URLField('Official Website')
    logo = models.ImageField(null=True)
    established = models.DateField(auto_now_add=True)
    country = CountryField(blank_label='Country')

    def __str__(self) -> str:
        return self.name


class Developer(CustomBaseModel):
    name = models.CharField(max_length=254, unique=True)
    slug = models.SlugField(max_length=254, unique=True, null=True, blank=True)
    description = models.CharField(max_length=500, default='')
    official_site = models.URLField('Official Website')
    logo = models.ImageField(null=True)
    established = models.DateField(auto_now_add=True)
    country = CountryField(blank_label='Country')

    def __str__(self) -> str:
        return self.name


class RatingSet(CustomBaseModel):
    game = models.OneToOneField("Game", on_delete=models.CASCADE, null=True, blank=True)
    dlc = models.OneToOneField("DLC", on_delete=models.CASCADE, null=True, blank=True)
    esrb_rating = models.ForeignKey("EsrbRating", null=True, on_delete=models.SET_NULL)
    pegi_rating = models.ForeignKey("PegiRating", null=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        if self.game is None:
            return self.dlc.name
        else:
            return self.game.name

    def user_rating_calc(self):
        user_ratings = UserRating.objects.filter(
            rating_set__game=self.game
        ).values_list("value", flat=True)
        num_ratings = len(user_ratings)
        avg_rating = sum(user_ratings) / num_ratings if user_ratings else 0
        if self.game is None:
            avg_all = (
                RatingSet.objects.filter(dlc=self.game).aggregate(
                    Avg("userrating__value")
                )["userrating__value__avg"]
                or 0
            )
        else:
            avg_all = (
                RatingSet.objects.filter(game=self.game).aggregate(
                    Avg("userrating__value")
                )["userrating__value__avg"]
                or 0
            )
        bayesian_avg = (avg_all * num_ratings + avg_rating) / (num_ratings + 1)
        return round(bayesian_avg * 2) / 2


class EsrbRating(CustomBaseModel):
    name = models.CharField(max_length=254, unique=True)
    slug = models.SlugField(max_length=254, unique=True, null=True, blank=True)
    image = models.ImageField(null=True)

    def __str__(self) -> str:
        return self.name


class PegiRating(CustomBaseModel):
    name = models.CharField(max_length=254, unique=True)
    slug = models.SlugField(max_length=254, unique=True, null=True, blank=True)
    image = models.ImageField(null=True)

    def __str__(self) -> str:
        return self.name


class UserRating(CustomBaseModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    rating_set = models.ForeignKey("RatingSet", on_delete=models.CASCADE)
    value = models.IntegerField(default='0',
        choices=[(0, '0 - None'), (1, "1 - Awful"), (2, "2 - Bad"), (3, "3 - Average"), (4, "4 - Good"), (5, "5 - Very Good")]
    )

    class Meta:
        unique_together = (
            "user",
            "rating_set",
        )  # each user can only rate a game once in a rating set

    def __str__(self):
        return f"{self.rating_set.game} - {self.user.username}"


class Platform(CustomBaseModel):
    name = models.CharField(max_length=254, unique=True)
    slug = models.SlugField(max_length=254, unique=True, null=True, blank=True)
    icon = models.ImageField(null=True, blank=True)
    description = models.CharField(max_length=500, default='')
    official_site = models.URLField('Official Website')
    logo = models.ImageField(null=True)
    established = models.DateField(auto_now_add=True)
    country = CountryField(blank_label='Country')

    def __str__(self) -> str:
        return self.name


class Tag(CustomBaseModel):
    name = models.CharField(max_length=254, unique=True)
    slug = models.SlugField(max_length=254, unique=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class Feature(CustomBaseModel):
    name = models.CharField(max_length=254, unique=True)
    slug = models.SlugField(max_length=254, unique=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class Media(CustomBaseModel):
    class Meta:
        verbose_name_plural = "Media"

    class MediaUseChoices(models.TextChoices):
        COVER = "COVER", ("Cover Image")
        LANDING = "LANDING", ("Landing Image")
        PREVIEW = "PREVIEW", ("Preview Media")
        OTHER = "OTHER", ("Other Media")

    name = models.CharField(max_length=254, unique=True)
    slug = models.SlugField(max_length=254, unique=True, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    file = models.ImageField(null=True, blank=True)
    media_type = models.CharField(
        max_length=6, null=True, choices=[("image", "Image"), ("video", "Video")]
    )
    media_use = models.CharField(
        max_length=24, default=MediaUseChoices.OTHER, choices=MediaUseChoices.choices
    )
    media_ext = models.CharField(max_length=6, null=True, blank=True)
    description = models.CharField(null=True, max_length=526)

    def __str__(self) -> str:
        return self.name


@receiver(pre_save, sender=Media)
def receiver(instance, *args, **kwargs):

    if instance.file._file is not None:  # If a file is being uploaded
        _, new_file_extension = os.path.splitext(instance.file._file.name)
        new_file_extension = new_file_extension.replace(".", "")

    if instance.file.name is not None and len(instance.file.name) != 0:
        _, curr_file_extension = os.path.splitext(instance.file.name)
        curr_file_extension = curr_file_extension.replace(".", "")

    if (
        len(instance.file.name) != 0
        and instance.media_ext is not None
        and instance.file._file is None
    ):
        # File exists, there is a media extension, and no new file is coming in.
        if curr_file_extension != instance.media_ext:
            # Auto-fill media extension.
            instance.media_ext = curr_file_extension
    elif instance.media_ext is None:
        # There is no media extension.
        if instance.file and instance.file._file is not None:
            # , but there is a new file coming in.
            instance.media_ext = new_file_extension
        elif len(instance.file.name) != 0:
            # , but there's a file already.
            instance.media_ext = curr_file_extension
    elif instance.media_ext is not None and len(instance.file.name) == 0:
        # There is an extension but no file.
        instance.media_ext = None
    elif instance.media_ext is not None and instance.file._file is not None:
        # There is an extension, but a new file is coming in.
        instance.media_ext = new_file_extension
    else:
        # None of the above applied.
        # If a cover photo exists already, don't save."
        pass
