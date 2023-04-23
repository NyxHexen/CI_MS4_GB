# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django import forms

# Local
from .models import Media
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class MediaForm(forms.ModelForm):
    """
    ModelForm for Media model
    """
    class Meta:
        model = Media
        fields = (
            'name',
            'url',
            'file',
            'media_type',
            'media_use',
            'description',
        )
