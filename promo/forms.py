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

    apply_to_game = forms.ModelMultipleChoiceField(
        queryset=Game.objects.filter(in_promo=False),
        widget=forms.SelectMultiple,
        required=False,
    )

    apply_to_dlc = forms.ModelMultipleChoiceField(
        queryset=DLC.objects.filter(in_promo=False),
        widget=forms.SelectMultiple,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """
        Add better placeholders
        """
        super().__init__(*args, **kwargs)

        self.fields['apply_to_game'].label = 'Available Games'
        self.fields['apply_to_dlc'].label = 'Available DLCs'
