# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.db import models
from django.utils.text import slugify
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class CustomBaseModel(models.Model):
    """
    Custom Model to help follow DRY rules by
    overriding Model methods in once place.
    """

    class Meta:
        abstract = True

    def model_name(self):
        return self._meta.model_name

    def __init__(self, *args, **kwargs):
        if (
            "slug" in self.__dict__
            ) and (
            self.slug is None or self.slug != slugify(self.name)
            ):
            self.slug = slugify(self.name)
        if "final_price" in self.__dict__ and self.final_price == 0:
            self.final_price = self.base_price
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        if (
            "slug" in self.__dict__
            ) and (
            self.slug is None or self.slug != slugify(self.name)
            ):
            self.slug = slugify(self.name)
        if (
            "final_price" in self.__dict__
            and self.final_price == 0
            and self.promo is None
        ):
            self.final_price = self.base_price
        super().save(*args, **kwargs)


class Media(CustomBaseModel):
    class Meta:
        verbose_name_plural = "Media"

    class MediaUseChoices(models.TextChoices):
        COVER = "COVER", ("Cover Image")
        LANDING = "LANDING", ("Landing Image")
        PREVIEW = "PREVIEW", ("Preview Media")
        OTHER = "OTHER", ("Other Media")

    name = models.CharField(
        max_length=254,
        unique=True
        )
    slug = models.SlugField(
        max_length=254,
        unique=True,
        null=True,
        blank=True
        )
    url = models.URLField(
        null=True,
        blank=True
        )
    file = models.ImageField(
        null=True,
        blank=True
        )
    media_type = models.CharField(
        max_length=6,
        null=True,
        choices=[
            ("image", "Image"),
            ("video", "Video")
            ]
        )
    media_use = models.CharField(
        max_length=24,
        default=MediaUseChoices.OTHER,
        choices=MediaUseChoices.choices
    )
    media_ext = models.CharField(
        max_length=6,
        null=True,
        blank=True
        )
    description = models.CharField(
        null=True,
        max_length=526
        )

    def __str__(self) -> str:
        return self.name
