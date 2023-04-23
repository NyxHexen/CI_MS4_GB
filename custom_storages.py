# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.conf import settings

# Third Party
from storages.backends.s3boto3 import S3Boto3Storage

# Included
import uuid
import os
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION

    def get_valid_name(self, name):
        # Modify the name of the file being uploaded
        serial_number = uuid.uuid4().hex[:10]
        _, ext = os.path.splitext(name)
        new_name = serial_number + ext
        return new_name