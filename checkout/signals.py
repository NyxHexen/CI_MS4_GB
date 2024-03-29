# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Local
from .models import OrderLineItem
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@receiver(post_save, sender=OrderLineItem)
def update_on_save(sender, instance, *args, **kwargs):
    """
    Update order_total on lineitem update/create
    """
    instance.order.update_total()
