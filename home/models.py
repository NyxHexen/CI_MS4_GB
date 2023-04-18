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

    if instance.file.name is not None and getattr(instance.file, 'name') not in [None, 0]:
        _, curr_file_extension = os.path.splitext(instance.file.name)
        curr_file_extension = curr_file_extension.replace(".", "")


    print(instance.file.__dict__)
    if (
        getattr(instance.file, 'name') not in [None, 0]
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
        elif getattr(instance.file, 'name') not in [None, 0]:
            # , but there's a file already.
            instance.media_ext = curr_file_extension
    elif instance.media_ext is not None and getattr(instance.file, 'name') in [None, 0]:
        # There is an extension but no file.
        instance.media_ext = None
    elif instance.media_ext is not None and instance.file._file is not None:
        # There is an extension, but a new file is coming in.
        instance.media_ext = new_file_extension
    else:
        # None of the above applied.
        # If a cover photo exists already, don't save."
        pass