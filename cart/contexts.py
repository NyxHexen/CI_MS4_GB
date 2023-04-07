from decimal import Decimal
from django.shortcuts import get_object_or_404
from .utils import *
from .models import Cart

from games.models import Game, DLC


def cart_contents(request):
    cart_items = list()
    total = Decimal('0.00')
    item_count = 0

    if not request.user.is_authenticated:
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
    else: 
        cart = Cart.objects.get_or_create(user=request.user)
        if bool(cart[0].cartitems.all()):
            for item in cart[0].cartitems.all():
                cart_items.append({
                    'item': item.game,    
                    'quantity': item.quantity,
                    'item_id': item.game.id if item.game.model_name() == 'game' else item.dlc.id
                })
                total += item.game.final_price if item.game.model_name() == 'game' else item.dlc.final_price
                item_count += 1
        

    context = {
        "cart_items": cart_items,
        "total" : total,
        "item_count" : item_count,
    }

    return context
