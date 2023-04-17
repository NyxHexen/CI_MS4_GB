from django import forms

from .models import Game, DLC, RatingSet


class GameForm(forms.ModelForm):
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
        print(self.fields['description'].widget.attrs)

        self.fields['description'].widget.attrs = {'rows': 5, 'cols': 40}
        self.fields['storyline'].widget.attrs = {'rows': 5, 'cols': 40}


class DLCForm(forms.ModelForm):
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
