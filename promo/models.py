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
    
    # Handles adding and removing from Promos
    def _update_games(self, **kwargs):
        match kwargs["action"]:
            case 'pre_remove':
                self.pre_remove = set(self.apply_to_game.all())
                self.pre_remove = self.pre_remove.union(set(self.apply_to_dlc.all()))
            case 'post_remove':
                self.post_remove = set(self.apply_to_game.all())
                self.post_remove = self.post_remove.union(set(self.apply_to_dlc.all()))
                for i in self.pre_remove.difference(self.post_remove):
                    game = get_or_none(kwargs['model'], id=i.id)
                    game.in_promo = False
                    game.promo = None
                    game.promo_percentage = 0
                    game.save()
            case 'pre_add':
                self.pre_add = set(self.apply_to_game.all())
                self.pre_add = self.pre_add.union(set(self.apply_to_dlc.all()))
            case 'post_add':
                self.post_add = set(self.apply_to_game.all())
                self.post_add = self.post_add.union(set(self.apply_to_dlc.all()))
                for i in self.post_add.difference(self.pre_add):
                    game = get_or_none(kwargs['model'], id=i.id)
                    game.in_promo = True
                    game.promo = self
                    game.save()

    def delete(self, using=None, keep_parents=False):
        games = (self.apply_to_game.all()).union(self.apply_to_dlc.all())
        for game in games:
            game.in_promo = False
            game.promo_percentage = 0
            game.save()
        return super().delete(using=using, 
                              keep_parents=keep_parents)
    
    def total_in_promo(self):
        return len(self.apply_to_game.all()) + len(self.apply_to_dlc.all())

    total_in_promo.short_description = "Games In Promo"

@receiver(m2m_changed, sender=Promo.apply_to_dlc.through)
def game_receiver(instance, *args, **kwargs):
    instance._update_games(**kwargs)


@receiver(m2m_changed, sender=Promo.apply_to_game.through)
def dlc_receiver(instance, *args, **kwargs):
    instance._update_games(**kwargs)


# Handles promo active status and percentage adjustment to final_price if active
@receiver(pre_save, sender=Promo)
def promo_price_apply(instance, *args, **kwargs):
    current = Promo.objects.filter(id=instance.id).all()[0].active
    updated = instance.active
    apply_discount(instance) if current < updated else remove_discount(instance) if current > updated else None


def apply_discount(instance):
    for queryset in [instance.apply_to_game.all(), instance.apply_to_dlc.all()]:
        for item in queryset:
            final_price = Decimal(round(item.base_price * (1 + (Decimal(item.promo_percentage) / 100 * -1 )), 2))
            queryset.filter(id=item.id).update(final_price=final_price)


def remove_discount(instance):
    for queryset in [instance.apply_to_game.all(), instance.apply_to_dlc.all()]:
        for item in queryset:
            final_price = item.base_price
            queryset.filter(id=item.id).update(final_price=final_price)