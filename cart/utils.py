from django.core.signing import Signer, BadSignature
import json


def sign_and_set_cart(request, cart):
    cart = json.dumps(cart)
    signer = Signer()
    cart_signed = signer.sign(cart)
    request.session['cart'] = {'cart_signed': cart_signed}
    return cart_signed

def get_and_unsign_cart(request):
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

