from django.shortcuts import render, redirect
from games.models import Game, DLC
from .utils import sign_and_set_cart, get_and_unsign_cart


# Create your views here.
def view_cart(request):
    context = {
    }
    return render(request, 'cart/index.html', context)


def cart_add(request, model_name, game_id):
    if not request.user.is_authenticated:
        game = Game.objects.filter(id=game_id) if model_name == 'game' else DLC.objects.filter(id=game_id)
        quantity = int(request.POST.get('quantity'))
        redirect_url = request.POST.get('redirect_url')

        cart = get_and_unsign_cart(request)

        if game_id in cart:
            cart[game_id]['quantity'] += quantity
        else:
            cart[game_id] = {'model': model_name, 'quantity': quantity }

        sign_and_set_cart(request, cart)
    return redirect(redirect_url)
