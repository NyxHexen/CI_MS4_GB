from django import template
from promo.models import Promo

register = template.Library()

@register.filter
def promo_games(name):
    try:
        promo = Promo.objects.filter(name=name)
        games = promo[0].apply_to_game.all().values('id', 'name', 'slug',
                                                         'base_price', 'promo_percentage',
                                                         'final_price')
        dlc = promo[0].apply_to_dlc.all().values('id', 'name', 'slug',
                                                         'base_price', 'promo_percentage',
                                                         'final_price')
        return games.union(dlc)
    except Exception as e:
        return None
