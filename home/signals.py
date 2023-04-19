from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Media

import os


@receiver(pre_save, sender=Media)
def media_control(instance, *args, **kwargs):

    if instance.file._file is not None:  # If a file is being uploaded
        _, new_file_extension = os.path.splitext(instance.file._file.name)
        new_file_extension = new_file_extension.replace(".", "")

    if instance.file.name is not None and getattr(instance.file, 'name') not in [None, 0]:
        _, curr_file_extension = os.path.splitext(instance.file.name)
        curr_file_extension = curr_file_extension.replace(".", "")

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
        pass