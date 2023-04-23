# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail

# Local
from ci_ms4_gamebox.utils import get_or_none
from cart.utils import get_and_unsign_cart
from cart.models import Cart
from cart.contexts import cart_contents
from games.models import Game, DLC
from profiles.models import UserProfile
from .models import Order, OrderLineItem
from .forms import OrderForm

# Third-party
import os
import stripe
import random
import json
import uuid
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Create your views here.
def checkout(request):
    """
    View to render 'checkout' page, and handle OrderForm().
    """
    if not request.user.is_authenticated:
        cart = get_and_unsign_cart(request)
        if len(cart) == 0:
            messages.error(
                request,
                "You cannot checkout with an empty cart!"
                )
            return redirect(reverse("cart"))

    else:
        cart = Cart.objects.get_or_create(user=request.user)[0]
        if cart.cartitems.count() == 0:
            messages.error(
                request,
                "You cannot checkout with an empty cart!"
                )
            return redirect(reverse("cart"))

    if request.user.is_authenticated:
        billing_addr = get_or_none(UserProfile, user=request.user)
        if billing_addr is not None:
            form_data = {
                "full_name": (
                    f'{billing_addr.user.first_name}' +
                    f' {billing_addr.user.last_name}'
                ),
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
        billing_addr = None
        order_form = OrderForm()

    if request.method == "POST":
        order_form = OrderForm(request.POST)

        if order_form.is_valid():
            if request.user.is_authenticated and "save-info" in request.POST:
                for data in order_form.cleaned_data:
                    if hasattr(billing_addr, "default_" + data):
                        match = getattr(billing_addr, "default_" + data)
                        if order_form.cleaned_data[data] != match:
                            setattr(
                                billing_addr,
                                "default_" + data,
                                order_form.cleaned_data[data]
                                )
                            billing_addr.save()

            order = order_form.save(commit=False)
            order.stripe_pid = request.POST.get(
                'client_secret'
                ).split('_secret')[0]
            order.original_cart = json.dumps(
                cart_contents(request)['list_cart']
                )
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
                            game=(
                                game
                                if item_data["model"] == "game"
                                else None
                                ),
                            dlc=(
                                game
                                if item_data["model"] == "dlc"
                                else None
                                ),
                            quantity=item_data["quantity"],
                        )
                        order_line_item.save()
                    except ObjectDoesNotExist:
                        messages.error(
                            request,
                            (
                                "Uh-oh. One of the products has gone missing. \
                                Please try again later, and if the issue \
                                persists don't hesitate to contact us!"
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
                            "Uh-oh. One of the products has gone missing. "
                            "Please try again later, and if the issue persists\
                            don't hesitate to contact us!"
                        ),
                    )
                    order.delete()
                    return redirect(reverse("view_cart"))

            request.session["save_info"] = "save-info" in request.POST
            return redirect(
                reverse("checkout_success", args=[order.order_number])
                )
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
    Handle successful checkouts.
    """
    save_info = request.session.get("save_info")
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(
        request,
        f"Order successfully processed! \
          Your order number is {order_number}. A confirmation \
          email will be sent to {order.email}",
    )
    try:
        order_items = ""
        for item in order.lineitems.all():
            game = (
                item.game.name
                if item.game is not None
                else item.dlc.name
                )
            serial = uuid.uuid4().hex.upper()
            price = item.price
            item_info = f"""
                Name: {game}
                Price: {price}
                Serial Number: {serial}

                """
            order_items += item_info

        message = f"""
        Hi {order.full_name},

        Thank you for your purchase! Below you will find your complete order
        details:

        {order_items}

        Should you have any questions, please do not hesitate to contact us
        via e-mail at info@gamebox.com.

        Sincerely,
        The GameBOX team
        """

        send_mail(
            f"""\
            [GameBOX] Thank you for your purchase!\
            Enjoy! Order #: {order.order_number}\
            """,
            message,
            "info@gamebox.com",
            [request.user.email, ]
        )
    except Exception as e:
        print(e)
        messages.error(
            request,
            f"There has been an issue with your email confirmation.\
        Please contact us to resolve this error.",
        )

    if not request.user.is_authenticated:
        if "cart" in request.session:
            cart = get_and_unsign_cart(request)
            del request.session["cart"]
    else:
        try:
            cart = Cart.objects.get(user=request.user)
            cart.delete()
        except Exception:
            messages.info(
                request,
                "Woops! Our server had an accident. \
                Not to worry! Your order \
                has been processed either way.",
            )

    try:
        games = Game.objects.all()
        dlcs = DLC.objects.all()
    except Exception:
        messages.error(
            request,
            "Some of our games have escaped! \
             Give us a minute and we'll bring them right back.")

    purchased_games = [i.game or i.dlc for i in order.lineitems.all()]
    unowned_games = (
        [game for game in games if game not in purchased_games] +
        [dlc for dlc in dlcs if dlc not in purchased_games]
    )
    samples_num = (
        5
        if len(unowned_games) > 5
        else len(unowned_games)
        )
    suggested_games = random.sample(unowned_games, samples_num)

    context = {"order": order, "suggested_games": suggested_games}

    return render(request, "checkout/checkout-success.html", context)


@require_POST
def create_stripe_intent(request):
    """
    Creates a PaymentIntent object in Stripe for the total amount of the
    current cart.

    Args:
        request: An HttpRequest.
    Returns:
        A JsonResponse object containing the client secret.
    Raises:
        HttpResponse: If an error occurs while creating the PaymentIntent
                      object.
    """
    try:
        current_cart = cart_contents(request)
        amount = current_cart["total"]
        stripe_amount = round(amount * 100)

        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

        intent = stripe.PaymentIntent.create(
            amount=stripe_amount,
            currency=settings.STRIPE_CURRENCY,
            automatic_payment_methods={"enabled": True},
        )
        return JsonResponse(
            {"client_secret": intent.client_secret}
            )
    except Exception as e:
        messages.error(
            request,
            "We're experiencing some technical difficulties with the card\
            payment system. Please try again later, and if the issue persists,\
            please contact customer support for assistance.",
        )
        return HttpResponse(content=e, status=400)


@require_POST
def modify_stripe_intent(request):
    """
    Modifies a PaymentIntent object in Stripe with additional metadata to
    include the guest/user's billing information and cart in the Stripe intent.

    Args:
        request: An HttpRequest object.
    Returns:
        An HttpResponse object with a 200 status code.
    Raises:
        HttpResponse: An error occurred while modifying the PaymentIntent
                      object.
    """
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
            "We're unable to process your payment at this time.\
                Please try again later, and if the issue persists,\
                      please contact customer support for assistance.",
        )
        return HttpResponse(content=e, status=400)
