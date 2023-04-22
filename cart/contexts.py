from decimal import Decimal
from django.shortcuts import get_object_or_404

from games.models import Game, DLC
from .utils import *
from .models import Cart


def cart_contents(request):
    """
    View to display cart contents to the user.
    """
    cart_items = list()
    total = Decimal('0.00')
    item_count = 0

    if not request.user.is_authenticated:
        cart = get_and_unsign_cart(request)
        if bool(cart):
            for key, value in cart.items():
                model = (
                    Game
                    if value['model'] == 'game'
                    else DLC
                    )
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
                model = Game if item.game else DLC
                cart_items.append({
                    'item': item.game if model is Game else item.dlc,    
                    'quantity': item.quantity,
                    'item_id': item.game.id if model is Game else item.dlc.id
                })
                total += (
                    item.game.final_price * item.quantity
                    if model is Game
                    else item.dlc.final_price * item.quantity
                    )
                item_count += 1
    
            
    list_cart = {
        "line_items": [],
        "cart_total": float(),
    }

    for item in cart_items:
        list_cart["line_items"].append(
            {
                "item": item["item"].name,
                "item_id": item["item_id"],
                "quantity": item["quantity"],
            }
        )
        list_cart["cart_total"] += float(item["item"].final_price)

    context = {
        "cart_items": cart_items,
        "total" : total,
        "item_count" : item_count,
        "list_cart": list_cart,
    }

    return context
