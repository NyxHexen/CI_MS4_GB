from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings

from cart.utils import get_and_unsign_cart
from cart.models import Cart
from cart.contexts import cart_contents
from .forms import OrderForm

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
    current_cart = cart_contents(request)
    amount = current_cart['total']
    stripe_amount = round(amount * 100)

    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

    intent = stripe.PaymentIntent.create(
        amount=stripe_amount,
        currency=settings.STRIPE_CURRENCY,
        automatic_payment_methods={
            'enabled': True
        }
    )
    return JsonResponse({'client_secret': intent.client_secret})
