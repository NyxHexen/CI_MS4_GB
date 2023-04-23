# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django import forms

# Local
from .models import Game, DLC, RatingSet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class GameForm(forms.ModelForm):
    """
    ModelForm class for Games
    """
    class Meta:
        model = Game
        fields = (
            'name',
            'description',
            'storyline',
            'genres',
            'publishers',
            'developers',
            'release_date',
            'description',
            'platforms',
            'tags',
            'features',
            'is_featured',
            'carousel',
            'base_price',
            'media',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['description'].widget.attrs = {'rows': 5, 'cols': 40}
        self.fields['storyline'].widget.attrs = {'rows': 5, 'cols': 40}


class DLCForm(forms.ModelForm):
    """
    ModelForm class for DLCs
    """
    class Meta:
        model = DLC
        fields = (
            'required_game',
            'name',
            'description',
            'storyline',
            'genres',
            'publishers',
            'developers',
            'release_date',
            'description',
            'platforms',
            'tags',
            'features',
            'media',
            'is_featured',
            'carousel',
            'base_price',
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget.attrs = {'rows': 5, 'cols': 40}
        self.fields['storyline'].widget.attrs = {'rows': 5, 'cols': 40}


class RatingForm(forms.ModelForm):
    """
    ModelForm class for RatingSet
    """
    class Meta:
        model = RatingSet
        fields = (
            'game',
            'dlc',
            'esrb_rating',
            'pegi_rating',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['esrb_rating'].label = 'ESRB Rating'
        self.fields['pegi_rating'].label = 'PEGI Rating'
