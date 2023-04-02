from django import template
from promo.models import Promo
from decimal import Decimal

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

@register.filter
def calc_promo_price(price, increase):
    try:
        promo_calc = round(price * (1 + (Decimal(increase) / 100 * -1 )), 2)
        return promo_calc
    except Exception:
        return None
    

@register.filter
def slide_split(iter, request):
    """ Group items of 'iter' into batches of 'size'."""
    if request.user_agent.is_tablet:
        size = 3
    elif request.user_agent.is_mobile:
        size = 1
    else:
        size = 4
    return [iter[i:i+size] for i in range(0, len(iter), size)]