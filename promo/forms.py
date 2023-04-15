from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from games.models import Game, DLC

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from django.forms.widgets import SplitDateTimeWidget

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
