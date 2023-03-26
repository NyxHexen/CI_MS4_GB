from django.db import models
from django.db.models.signals import m2m_changed, pre_save
from datetime import datetime, time, timedelta
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from decimal import Decimal

from games.models import CustomBaseModel, Media
from ci_ms4_gamebox.utils import get_or_none


class Promo(CustomBaseModel):
    active = models.BooleanField(default=False)
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, null=True, blank=True)
    start_date = models.DateTimeField(null=True, default=datetime.combine(datetime.now().date(), time(hour=0, minute=1)))
    end_date = models.DateTimeField(null=True, default=datetime.combine(datetime.now() + timedelta(days=1), time(hour=0, minute=1)))
    apply_to_game = models.ManyToManyField('games.Game', related_name='mtm', blank=True)
    apply_to_dlc = models.ManyToManyField('games.DLC', related_name='mtm', blank=True)
    landing_page = models.BooleanField(default=False)
    media = models.ForeignKey(Media, null=True, blank=True, on_delete=models.SET_NULL)
    url = models.URLField(max_length=1024, null=True, blank=True)
    is_featured = models.BooleanField(default=False, null=True, blank=True)
    carousel = models.BooleanField(default=False, null=True, blank=True)
    short_description = models.TextField(max_length=512, null=True, blank=True)
    long_description = models.TextField(max_length=1024, null=True, blank=True)

    def __str__(self) -> str:
        return self.name
    
    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError('End date cannot be before start date.', code='invalid', params={'end_date': 'End date'})

    pre_add = None
    post_add = None
    pre_remove = None
    post_remove = None
    

    def delete(self, using=None, keep_parents=False):
        remove_discount(self)
        return super().delete(using=using, 
                              keep_parents=keep_parents)
    
    def total_in_promo(self):
        return len(self.apply_to_game.all()) + len(self.apply_to_dlc.all())

    total_in_promo.short_description = "Games In Promo"


# Controls actions that occur when a Promo becomes active/offline.
@receiver(pre_save, sender=Promo)
def promo_price_apply(instance, *args, **kwargs):
    promo = get_or_none(Promo, id=instance.id)
    if promo is not None:
        current = promo.active
        updated = instance.active
        apply_discount(instance) if current < updated else remove_discount(instance) if current > updated else None

# Applies the discount to all associated games/DLCs when a Promo becomes active.
# It calculates the final price and sets the promo and in_promo fields for each game/DLC.
def apply_discount(instance):
    for queryset in [instance.apply_to_game.all(), instance.apply_to_dlc.all()]:
        for item in queryset:
            final_price = Decimal(round(item.base_price * (1 + (Decimal(item.promo_percentage) / 100 * -1 )), 2))
            queryset.filter(id=item.id).update(final_price=final_price, promo=instance, in_promo=True)


# Removes the discount from all associated games/DLCs when a Promo becomes offline.
# It sets the final price back to the base price and clears the promo and in_promo fields for each game/DLC.
def remove_discount(instance):
    for queryset in [instance.apply_to_game.all(), instance.apply_to_dlc.all()]:
        for item in queryset:
            final_price = item.base_price
            queryset.filter(id=item.id).update(final_price=final_price, promo_percentage=0, in_promo=False, promo=None)