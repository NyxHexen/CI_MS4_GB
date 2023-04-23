# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.urls import path

# Local
from . import views
from .webhooks import webhook

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('_payment_intent_create/', views.create_stripe_intent, name='create_stripe_intent'),
    path('_payment_intent_modify/', views.modify_stripe_intent, name='modify_stripe_intent'),
    path('success/<order_number>', views.checkout_success, name='checkout_success'),
    # Webhooks
    path('wh/', webhook, name='webhook'),
]