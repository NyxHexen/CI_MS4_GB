from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from ci_ms4_gamebox.utils import get_or_none
from cart.utils import get_and_unsign_cart
from cart.models import Cart
from cart.contexts import cart_contents
from games.models import Game, DLC
from profiles.models import UserProfile

from .models import Order, OrderLineItem
from .forms import OrderForm

import os
import stripe
import random
import json


# Create your views here.
def checkout(request):
    if not request.user.is_authenticated:
        cart = get_and_unsign_cart(request)
        if len(cart) == 0:
            messages.error(request, "Your cart appears to be barren at present!")
            return redirect(reverse("cart"))

    else:
        cart = Cart.objects.get_or_create(user=request.user)[0]
        if cart.cartitems.count() == 0:
            messages.error(request, "Your cart appears to be barren at present!")
            return redirect(reverse("cart"))

    if request.user.is_authenticated:
        billing_addr = get_or_none(UserProfile, user=request.user)
        if billing_addr is not None:
            form_data = {
                "full_name": f'{billing_addr.user.first_name} {billing_addr.user.last_name}',
                "email": billing_addr.user.email,
                "phone_number": billing_addr.default_phone_number,
                "country": billing_addr.default_country,
                "postcode": billing_addr.default_postcode,
                "town_or_city": billing_addr.default_town_or_city,
                "street_address1": billing_addr.default_street_address1,
                "street_address2": billing_addr.default_street_address2,
                "county": billing_addr.default_county,
            }
            order_form = OrderForm(form_data)
    else: 
        order_form = OrderForm()

    if request.method == "POST":
        if billing_addr is not None:
            form_data = {
                "full_name": request.POST["full_name"],
                "email": request.POST["email"],
                "phone_number": request.POST["phone_number"],
                "country": request.POST["country"],
                "postcode": request.POST["postcode"],
                "town_or_city": request.POST["town_or_city"],
                "street_address1": request.POST["street_address1"],
                "street_address2": request.POST["street_address2"],
                "county": request.POST["county"],
            }
            order_form = OrderForm(form_data)

        if order_form.is_valid():
            if request.user.is_authenticated and "save-info" in request.POST:
                for data in order_form.cleaned_data:
                    if hasattr(billing_addr, "default_" + data):
                        match = getattr(billing_addr, "default_" + data)
                        if data != match:
                            setattr(billing_addr, "default_" + data, order_form.cleaned_data[data])
                            billing_addr.save()
            
            order = order_form.save(commit=False)
            order.stripe_pid = request.POST.get('client_secret').split('_secret')[0]
            order.original_cart = json.dumps(cart_contents(request)['list_cart'])
            order.save()
            if not request.user.is_authenticated:
                for item_id, item_data in cart.items():
                    try:
                        game = (
                            Game.objects.get(id=item_id)
                            if item_data["model"] == "game"
                            else DLC.objects.get(id=item_id)
                        )
                        order_line_item = OrderLineItem(
                            order=order,
                            game=game if item_data["model"] == "game" else None,
                            dlc=game if item_data["model"] == "dlc" else None,
                            quantity=item_data["quantity"],
                        )
                        order_line_item.save()
                    except ObjectDoesNotExist:
                        messages.error(
                            request,
                            (
                                "Uh-oh. One of the products has gone missing. "
                                "Better give us a call!"
                            ),
                        )
                        order.delete()
                        return redirect(reverse("view_cart"))
            else:
                try:
                    cart = Cart.objects.get(user=request.user)
                    for i in cart.cartitems.all():
                        order_line_item = OrderLineItem(
                            order=order,
                            game=i.game or None,
                            dlc=i.dlc or None,
                            quantity=i.quantity,
                        )
                        order_line_item.save()
                except ObjectDoesNotExist:
                    messages.error(
                        request,
                        (
                            "System Malfunction! Please try again later!"
                        ),
                    )
                    order.delete()
                    return redirect(reverse("view_cart"))

            request.session["save_info"] = "save-info" in request.POST
            return redirect(reverse("checkout_success", args=[order.order_number]))
        else:
            messages.error(
                request,
                "There was an error with your form. \
                           Please double check your information.",
            )

    context = {
        "order_form": order_form,
        "stripe_public_key": os.environ.get("STRIPE_PUBLISHABLE_KEY"),
    }
    return render(request, "checkout/index.html", context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    save_info = request.session.get("save_info")
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(
        request,
        f"Order successfully processed! \
                    Your order number is {order_number}. A confirmation \
                    email will be sent to {order.email}",
    )
    if not request.user.is_authenticated:
        if "cart" in request.session:
            cart = get_and_unsign_cart(request)
            del request.session["cart"]
    else:
        try:
            cart = Cart.objects.get(user=request.user)
            cart.delete()
        except Exception as e:
            messages.info(
                request,
                "Woops! Our server had an accident \
                           while trying to delete your old cart. Not to worry! Your order \
                          has been processed either way.",
            )

    games = Game.objects.all()
    dlcs = DLC.objects.all()

    purchased_games = [i.game or i.dlc for i in order.lineitems.all()]
    unowned_games = [j for j in games if j not in purchased_games] + [
        j for j in dlcs if j not in purchased_games
    ]
    samples_num = 5 if len(unowned_games) > 5 else len(unowned_games)
    suggested_games = random.sample(unowned_games, samples_num)

    context = {"order": order, "suggested_games": suggested_games}

    return render(request, "checkout/checkout-success.html", context)


@require_POST
def create_stripe_intent(request):
    current_cart = cart_contents(request)
    amount = current_cart["total"]
    stripe_amount = round(amount * 100)

    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

    intent = stripe.PaymentIntent.create(
        amount=stripe_amount,
        currency=settings.STRIPE_CURRENCY,
        automatic_payment_methods={"enabled": True},
    )
    return JsonResponse({"client_secret": intent.client_secret})


@require_POST
def modify_stripe_intent(request):
    try:
        pid = json.loads(request.body)["client_secret"].split("_secret")[0]
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
        stripe.PaymentIntent.modify(
            pid,
            metadata={
                "username": request.user.id,
                "save_info": json.loads(request.body)["save_info"],
                "cart": json.dumps(cart_contents(request)["list_cart"]),
            },
        )
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(
            request,
            "We're unable to process your payment at this time. Please try again later, and if the issue persists, please contact customer support for assistance.",
        )
        return HttpResponse(content=e, status=400)
