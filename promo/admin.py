# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.contrib import admin, messages

# Internal
from ci_ms4_gamebox.utils import get_or_none
from games.models import Game, DLC

# Local
from .models import Promo

# Included
import re
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class PromoAdminModel(admin.ModelAdmin):
    def save_model(self, request, *args, **kwargs):
        if request.method == "POST":
            for key, value in request.POST.items():
                if re.match(r"gamedata-\d+_[a-zA-Z0-9_]+", key):
                    # Value is sent as promo_percentage-(game_id)_(model_name)
                    # To help tell them apart as both DB start from 1
                    id = int(key.split("-")[-1].split("_")[0])
                    model = key.split("-")[-1].split("_")[-1]
                    try:
                        game_set = set()
                        game = (
                            get_or_none(Game, id=id)
                            if model == "game"
                            else get_or_none(DLC, id=id)
                            )
                        if game is not None:
                            game_set.add(game)
                    except Exception as e:
                        messages.error(request, f'{e}')
                    for item in game_set:
                        if item.promo_percentage != int(value):
                            item.promo_percentage = int(value)
                            item.save()
        return super().save_model(request, *args, **kwargs)


class PromoAdmin(PromoAdminModel):
    change_form_template = "admin/promo_template.html"
    filter_horizontal = [
        'apply_to_game',
        'apply_to_dlc',
        ]
    list_display = [
        'id',
        'name',
        'slug',
        'active',
        'url',
        'total_in_promo',
        'is_featured',
        'carousel',
        'start_date',
        'end_date'
        ]
    readonly_fields = [
        'slug',
        ]

admin.site.register(Promo, PromoAdmin)