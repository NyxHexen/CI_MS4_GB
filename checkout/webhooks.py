from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from checkout.webhook_handler import StripeWH_Handler

import stripe


@require_POST
@csrf_exempt
def webhook(request):
    """
    Listen to webhooks from Stripe
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    wh_secret = settings.STRIPE_WH_SECRET

    event = None
    payload = request.body
    sig_header = request.headers["STRIPE_SIGNATURE"]

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            wh_secret,
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e
    except Exception as e:
        return HttpResponse(content=e, status=400)

    handler = StripeWH_Handler(request)

    event_map = {
        "payment_intent.succeeded": handler.handle_payment_intent_succeeded,
        "payment_intent.payment_failed": handler.handle_payment_intent_payment_failed,
    }

    event_type = event["type"]

    event_handler = event_map.get(event_type, handler.handle_event)
    response = event_handler(event)
    return response
