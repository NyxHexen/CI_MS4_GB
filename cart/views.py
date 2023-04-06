from django.shortcuts import render, redirect
from games.models import Game, DLC
from .utils import sign_and_set_cart, get_and_unsign_cart
from django.http import JsonResponse
import json


# Create your views here.
def view_cart(request):
    context = {
    }
    return render(request, 'cart/index.html', context)


def cart_add(request, model_name, game_id):
    if not request.user.is_authenticated:
        game = Game.objects.filter(id=game_id) if model_name == 'game' else DLC.objects.filter(id=game_id)
        quantity = int(request.POST.get('quantity'))

        cart = get_and_unsign_cart(request)

        if game_id in cart:
            cart[game_id]['quantity'] += quantity
        else:
            cart[game_id] = {'model': model_name, 'quantity': quantity }

        sign_and_set_cart(request, cart)

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
