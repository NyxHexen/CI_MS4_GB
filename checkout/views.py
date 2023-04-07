from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from cart.utils import sign_and_set_cart, get_and_unsign_cart
from cart.models import Cart
from .forms import OrderForm

# Create your views here.
def checkout(request):
    if not request.user.is_authenticated:
        cart = get_and_unsign_cart(request)
        if cart[0].length == 0:
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
    }
    return render(request, 'checkout/index.html', context)