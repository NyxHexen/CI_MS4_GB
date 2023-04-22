from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from .models import Order, OrderLineItem
from cart.models import Cart
from games.models import Game, DLC

import stripe
import json
import time


class StripeWH_Handler:
    """
    Handle Stripe webhooks
    """

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200
        )

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object
        pid = intent.id
        cart = json.loads(intent.metadata.cart)
        save_info = intent.metadata.save_info
        username = intent.metadata.username

        stripe_charge = stripe.Charge.retrieve(intent.latest_charge)

        billing_details = stripe_charge.billing_details
        grand_total = round(stripe_charge.amount / 100, 2)

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=billing_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=billing_details.phone,
                    country__iexact=billing_details.address.country,
                    town_or_city__iexact=billing_details.address.city,
                    street_address1__iexact=billing_details.address.line1,
                    order_total__iexact=grand_total,
                    original_cart=cart,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except ObjectDoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            return HttpResponse(
                content=f'Webhook received: {event["type"]}',
                status=200
            )
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=billing_details.name,
                    email=billing_details.email,
                    phone_number=billing_details.phone,
                    country=billing_details.address.country,
                    postcode=billing_details.address.postal_code,
                    town_or_city=billing_details.address.city,
                    street_address1=billing_details.address.line1,
                    street_address2=billing_details.address.line2,
                    county=billing_details.address.state,
                    order_total=grand_total,
                    original_cart=cart,
                    stripe_pid=pid,
                )
                if username == "AnonymousUser":
                    for item_id, item_data in cart.line_items:
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
                else:
                    cart = Cart.objects.get(user=username)
                    for i in cart.cartitems.all():
                        order_line_item = OrderLineItem(
                                order = order,
                                game = i.game or None,
                                dlc = i.dlc or None,
                                quantity = i.quantity,
                            )
                        order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500,
                )

        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200
            )

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200
            )
