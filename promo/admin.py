from django.contrib import admin, messages
from ci_ms4_gamebox.utils import get_or_none
from games.models import Game, DLC
from .models import Promo

import re

# Register your models here.

class PromoAdminModel(admin.ModelAdmin):
    def save_model(self, request, *args, **kwargs):
        """
        Hijacking a method to use 'request' to access custom-added input fields.
        """
        if request.method == "POST":
            for key, value in request.POST.items():
                if re.match(r"promo_percentage-\d+\b", key):
                    pk = int(key.split("-")[-1])
                    try:
                        game_set = set()
                        game = get_or_none(Game, id=pk)
                        dlc = get_or_none(DLC, id=pk)
                        if dlc is not None:
                            game_set.add(dlc)
                        elif (game is not None):
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
    filter_horizontal = ['apply_to_game', 'apply_to_dlc',]
    list_display = ['id', 'name', 'slug', 'url', 'total_in_promo', 
                    'featured', 'carousel', 'start_date', 'end_date' ]
    readonly_fields = ['slug',]

admin.site.register(Promo, PromoAdmin)