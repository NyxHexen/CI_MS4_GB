from django import forms

from games.models import Game, DLC
from .models import Promo


class PromoForm(forms.ModelForm):
    class Meta:
        model = Promo
        fields = (
            'active',
            'name',
            'start_date',
            'end_date',
            'apply_to_game',
            'apply_to_dlc',
            'landing_page',
            'media',
            'url',
            'is_featured',
            'carousel',
            'short_description',
            'long_description',
        )

    def __init__(self, *args, **kwargs):
        """
        Add better placeholders and ensure that only games shown are either in this Promo
        or not in one at all.
        """
        super().__init__(*args, **kwargs)

        self.fields['apply_to_game'].label = 'Available Games'
        self.fields['apply_to_dlc'].label = 'Available DLCs'
        
        promo_instance = kwargs.get('instance', None)
        if promo_instance:
            try:
                games = (
                    promo_instance.apply_to_game.all()
                    + Game.objects.filter(in_promo=False)
                )
                dlcs = (
                    promo_instance.apply_to_dlc.all()
                    + DLC.objects.filter(in_promo=False)
                )
                self.fields['apply_to_game'].queryset = games
                self.fields['apply_to_dlc'].queryset = dlcs
            except Exception:
                pass


