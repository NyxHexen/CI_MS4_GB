# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.dispatch import receiver
from django.db.models.signals import m2m_changed, pre_save

# Internal
from ci_ms4_gamebox.utils import get_or_none

# Local
from .models import Promo
from .utils import apply_discount, remove_discount
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Controls actions that occur when a Promo becomes active/offline.
@receiver(pre_save, sender=Promo)
def promo_price_apply(instance, *args, **kwargs):
    """
    Pre-Save receiver to handle discount application.

    Args:
        pre_save (signal): Signal on which the receiver activates.
        sender (model): Model which sends this signal.

    Returns:
        None
    """
    promo = get_or_none(
        Promo,
        id=instance.id
        )
    if promo is not None:
        current = promo.active
        updated = instance.active
        (apply_discount(instance)
         if current < updated
         else remove_discount(instance)
         if current > updated
         else None)


@receiver(m2m_changed, sender=Promo.apply_to_game.through)
def game_change(instance, *args, **kwargs):
    """
    Additional m2m save logic to manage Game model.

    Args:
        pre_save (signal): Signal on which the receiver activates.
        sender (model): Field which sends this signal.

    Returns:
        None
    """
    instance._update_promo_items(**kwargs)


@receiver(m2m_changed, sender=Promo.apply_to_dlc.through)
def dlc_change(instance, *args, **kwargs):
    """
    Additional m2m save logic to manage DLC model.

    Args:
        pre_save (signal): Signal on which the receiver activates.
        sender (model): Field which sends this signal.

    Returns:
        None
    """
    instance._update_promo_items(**kwargs)
