from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.signals import user_logged_in

from .utils import get_and_unsign_cart
from games.models import Game, DLC
from .models import Cart

@receiver(user_logged_in, sender=User)
def merge_cart(sender, request, user, **kwargs):
    """
    Merge the contents of a guest's session cart with a new database cart
    if they log in with their user account.

    Args:
        sender: The sender of the signal.
        request: The request object.
        user: The user object.

    Returns:
        None
    """
    session_cart = get_and_unsign_cart(request)
    db_cart = Cart.objects.get_or_create(user=request.user)
    for game_id in session_cart:
        model = session_cart[game_id]['model']
        quantity = session_cart[game_id]['quantity']
        game = (
            Game.objects.get(id=game_id)
            if model == 'game'
            else DLC.objects.get(id=game_id)
        )
        cart_items = db_cart[0].cartitems.all()
        if game in [i.game or i.dlc for i in cart_items]:
                item = cart_items.get(game=game)
                if not item.quantity == quantity:
                    item.quantity = quantity
                item.save()
        else: 
            if game.model_name() == 'game':
                db_cart[0].cartitems.create(
                     game=game,
                     quantity=quantity, 
                     price=game.final_price,
                     )
            else:
                db_cart[0].cartitems.create(
                     dlc=game, 
                     quantity=quantity, 
                     price=game.final_price,
                     )