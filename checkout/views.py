from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum

from ci_ms4_gamebox.utils import get_or_none
from cart.utils import get_and_unsign_cart
from cart.models import Cart
from games.models import Game, DLC
from .forms import OrderForm
from decimal import Decimal

import os
import stripe


# Create your views here.
def checkout(request):
    if not request.user.is_authenticated:
        cart = get_and_unsign_cart(request)
        if len(cart) == 0:
            messages.error(request, "Your cart appears to be barren at present!")
            return redirect(reverse('cart'))

    else:
        cart = Cart.objects.get_or_create(user=request.user)
        if cart[0].cartitems.count() == 0:
            messages.error(request, "Your cart appears to be barren at present!")
            print("Empty!")
            return redirect(reverse('cart'))
    
    order_form = OrderForm()

    context = {
        'order_form': order_form,
        'stripe_public_key': os.environ.get('STRIPE_PUBLISHABLE_KEY'),
    }
    return render(request, 'checkout/index.html', context)

@require_POST
def create_payment(request):
    amount = int()
    if not request.user.is_authenticated:
        cart = get_and_unsign_cart(request)
        for key, value in cart.items():
            model = Game if value['model'] == 'game' else DLC
            game = get_or_none(model, id=key)
            amount += Decimal(game.final_price)
        amount = amount * 100
    currency = 'gbp'

    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

    intent = stripe.PaymentIntent.create(
        amount=amount.to_integral(),
        currency=currency,
        automatic_payment_methods={
            'enabled': True
        }
    )
    return JsonResponse({'data': intent.client_secret})
