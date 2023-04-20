from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages

from games.models import Game, DLC
from .models import Cart
from .utils import sign_and_set_cart, get_and_unsign_cart

import json


# Create your views here.
def view_cart(request):
    context = {
    }
    return render(request, 'cart/index.html', context)


def cart_add(request, model_name, game_id):
    redirect_url = request.POST.get('redirect_url')

    try:
        game = Game.objects.get(id=game_id) if model_name == 'game' else DLC.objects.get(id=game_id)
    except Exception:
        messages.error(request, 'We couldn\'t add this game to your cart. \
                       Please try again later!')
        return redirect(redirect_url)
         
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
                item = cart_items.get(game=game) if model_name == 'game' else cart_items.get(dlc=game)
                item.quantity += quantity
                item.save()
        else: 
            if game.model_name() == 'game':
                cart[0].cartitems.create(game=game, quantity=quantity, price=game.final_price)
            else:
                cart[0].cartitems.create(dlc=game, quantity=quantity, price=game.final_price)
        
    messages.success(request, f'{ game.name } x{ quantity } has been added to your cart!')

    return redirect(redirect_url)


def cart_remove(request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            game = Game.objects.get(id=data['game_id']) if data['model_name'] == 'game' else DLC.objects.get(id=data['game_id'])
            if not request.user.is_authenticated:
                cart = get_and_unsign_cart(request)
                del cart[data['game_id']]
                sign_and_set_cart(request, cart)
            else:
                cart = Cart.objects.get_or_create(user=request.user)
                cart_items = cart[0].cartitems.all()
                if game.model_name() == 'game':
                    cart_items.get(game=game).delete()
                else:
                    cart_items.get(dlc=game).delete()
        except Exception:
            messages.error(request, 'We couldn\'t remove this game from your cart. \
                            Please try again later!')
            return JsonResponse({'success': False})
        return JsonResponse({'success': True})
