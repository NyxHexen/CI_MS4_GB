from django.shortcuts import render, redirect
from django.http import JsonResponse

from games.models import Game, DLC
from .models import Cart
from ci_ms4_gamebox.utils import get_or_none
from .utils import sign_and_set_cart, get_and_unsign_cart

import json


# Create your views here.
def view_cart(request):
    context = {
    }
    return render(request, 'cart/index.html', context)


def cart_add(request, model_name, game_id):
    game = Game.objects.get(id=game_id) if model_name == 'game' else DLC.objects.get(id=game_id)
    quantity = int(request.POST.get('quantity'))

    if not request.user.is_authenticated:
        cart = get_and_unsign_cart(request)

        if game_id in cart:
            cart[game_id]['quantity'] += quantity
        else:
            cart[game_id] = {'model': model_name, 'quantity': quantity }

        sign_and_set_cart(request, cart)
    else:
        cart = Cart.objects.get_or_create(user=request.user)
        cart_items = cart[0].cartitems.all()
        if game in [i.game or i.dlc for i in cart_items]:
                item = cart_items.get(game=game)
                item.quantity += quantity
                item.save()
        else: 
            if game.model_name() == 'game':
                cart[0].cartitems.create(game=game, quantity=quantity, price=game.final_price)
            else:
                cart[0].cartitems.create(dlc=game, quantity=quantity, price=game.final_price)

    redirect_url = request.POST.get('redirect_url')
    return redirect(redirect_url)


def cart_remove(request):
        data = json.loads(request.body.decode('utf-8'))
        if not request.user.is_authenticated:
            game = Game.objects.filter(id=data['game_id']) if data['model_name'] == 'game' else DLC.objects.filter(id=data.game_id)
            # quantity = int(request.POST.get('quantity'))

        cart = get_and_unsign_cart(request)

        if data['action'] == 'remove':
             del cart[data['game_id']]
        elif data['action'] == 'update':
             pass

        sign_and_set_cart(request, cart)
        return JsonResponse({'success': True})