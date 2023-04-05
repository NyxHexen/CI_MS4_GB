from decimal import Decimal
from django.shortcuts import get_object_or_404
from .utils import *

from games.models import Game, DLC


def cart_contents(request):
    cart_items = list()
    total = Decimal('0.00')
    item_count = 0

    cart = get_and_unsign_cart(request)
    if bool(cart):
        for key, value in cart.items():
            model = Game if value['model'] == 'game' else DLC
            game = get_object_or_404(model, id=key)
            cart_items.append({
                'item': game,    
                'quantity': value['quantity'],
                'item_id': key
            })
            final_price = Decimal(game.final_price)
            total += final_price
            item_count += 1

    print(cart_items)

    context = {
        "cart_items": cart_items,
        "total" : total,
        "item_count" : item_count,
    }

    return context
