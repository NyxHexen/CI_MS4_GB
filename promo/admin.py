from django.contrib import admin
from ci_ms4_gamebox.utils import get_or_none
from .models import *

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
                        game = get_or_none(Game, id=pk).values('promo_percentage')
                        dlc = get_or_none(DLC, id=pk).values('promo_percentage')
                        game_list = game.union(dlc)
                        if game_list.promo_percentage != int(value):
                            game_list.promo_percentage = int(value)
                            game_list.save()
                    except Exception as e:
                        print(e)
        return super().save_model(request, *args, **kwargs)


class PromoAdmin(PromoAdminModel):
    change_form_template = "admin/promo_template.html"
    filter_horizontal = ['apply_to_game', 'apply_to_dlc',]
    list_display = ['id', 'name', 'slug', 'url', 'total_in_promo', 'start_date', 'end_date' ]
    readonly_fields = ['slug',]

admin.site.register(Promo, PromoAdmin)