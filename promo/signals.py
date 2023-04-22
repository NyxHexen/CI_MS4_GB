from django.dispatch import receiver
from django.db.models.signals import m2m_changed, pre_save

from ci_ms4_gamebox.utils import get_or_none
from .models import Promo
from .utils import apply_discount, remove_discount

# Controls actions that occur when a Promo becomes active/offline.
@receiver(pre_save, sender=Promo)
def promo_price_apply(instance, *args, **kwargs):
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
         else None
        )

@receiver(m2m_changed, sender=Promo.apply_to_game.through)
def game_change(instance, *args, **kwargs):
    instance._update_promo_items(**kwargs)


@receiver(m2m_changed, sender=Promo.apply_to_dlc.through)
def dlc_change(instance, *args, **kwargs):
    instance._update_promo_items(**kwargs)
