from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from cart.utils import get_and_unsign_cart
from cart.models import Cart
from cart.contexts import cart_contents
from games.models import Game, DLC

from .models import Order, OrderLineItem
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
        cart = Cart.objects.get_or_create(user=request.user)[0]
        if cart.cartitems.count() == 0:
            messages.error(request, "Your cart appears to be barren at present!")
            print("Empty!")
            return redirect(reverse('cart'))
    
    order_form = OrderForm()

    if request.method == 'POST':
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }

        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save()
            if not request.user.is_authenticated:
                for item_id, item_data in cart.items():
                    try:
                        game = Game.objects.get(id=item_id)
                        order_line_item = OrderLineItem(
                            order=order,
                            game=game if item_data['model'] == 'game' else None,
                            dlc=game if item_data['model'] == 'dlc' else None,
                            quantity=item_data['quantity'],
                        )
                        order_line_item.save()
                    except ObjectDoesNotExist:
                        messages.error(request, (
                            'Uh-oh. One of the products has gone missing. '
                            'Better give us a call!'
                        ))
                        order.delete()
                        return redirect(reverse('view_cart'))
                else:
                    print("Logged in! Log out to test log-out!")
            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(request, 'There was an error with your form. \
                           Please double check your information.')
                           
    context = {
        'order_form': order_form,
        'stripe_public_key': os.environ.get('STRIPE_PUBLISHABLE_KEY'),
    }
    return render(request, 'checkout/index.html', context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f"Order successfully processed! \
                    Your order number is {order_number}. A confirmation \
                    email will be sent to {order.email}")
    if not request.user.is_authenticated:
        if 'cart' in request.session:
            cart = get_and_unsign_cart(request)
            del request.session['cart']
    else:
        cart = Cart.objects.get_or_create(user=request.user)
        cart[0].delete()

    context = {
        'order': order,
    }

    return render(request, 'checkout/checkout-success.html', context)
    

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
