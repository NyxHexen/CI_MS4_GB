from datetime import datetime, time, timedelta

from decimal import Decimal
from django.utils import timezone

def default_start_datetime():
    now = timezone.now()
    return timezone.make_aware(
        datetime.combine(
            now.date(),
            time(hour=0, minute=1)),
            now.tzinfo
            )


def default_end_datetime():
    now = timezone.now()
    return timezone.make_aware(
        datetime.combine(
        now.date(),
        time(hour=0, minute=1)) + timedelta(days=1),
        now.tzinfo
        )


# Applies the discount to all associated games/DLCs when a Promo becomes active.
# It calculates the final price and sets the promo and in_promo fields for each game/DLC.
def apply_discount(instance):
    for queryset in [
        instance.apply_to_game.all(), instance.apply_to_dlc.all()
        ]:
        for item in queryset:
            final_price = Decimal(
                round(
                    item.base_price * (1 + (Decimal(item.promo_percentage) / 100 * -1)),
                    2,
                )
            )
            queryset.filter(id=item.id).update(
                final_price=final_price,
                promo=instance,
                in_promo=True
            )


# Removes the discount from all associated games/DLCs when a Promo becomes offline.
# It sets the final price back to the base price and clears the promo and in_promo fields for each game/DLC.
def remove_discount(instance):
    for queryset in [
        instance.apply_to_game.all(), instance.apply_to_dlc.all()
        ]:
        for item in queryset:
            final_price = item.base_price
            queryset.filter(id=item.id).update(
                final_price=final_price,
                promo_percentage=0,
                in_promo=False,
                promo=None
            )