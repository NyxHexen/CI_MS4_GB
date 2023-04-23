# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.core.signing import Signer, BadSignature

# Python
import json
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def sign_and_set_cart(request, cart):
    """
    Cache the cart data for the user and sign it
    Args:
        request (object): The request object
        cart (dict): The cart data to cache and sign
    Returns:
        str: The signed cart data
    """
    cart = json.dumps(cart)
    signer = Signer()
    cart_signed = signer.sign(cart)
    request.session['cart'] = {
        'cart_signed': cart_signed
        }
    return cart_signed


def get_and_unsign_cart(request):
    """
    Retrieve and unsign the cached cart data for the user
    Args:
        request (object): The request object
    Returns:
        dict: The unsigned cart data
    """
    cart_signed = request.session.get('cart', {})
    if "cart_signed" in cart_signed:
        cart_signed = cart_signed['cart_signed']
    if bool(cart_signed):
        signer = Signer()
        try:
            cart = signer.unsign(cart_signed)
            cart = json.loads(cart)
        except BadSignature:
            pass
    else:
        cart = {}
    return cart
