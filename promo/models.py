from django.db import models
from django.db.models import Max
from django.db.models.signals import m2m_changed, pre_save
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from decimal import Decimal

from games.models import CustomBaseModel, DLC, Game
from home.models import Media
from ci_ms4_gamebox.utils import get_or_none
from .utils import default_start_datetime, default_end_datetime


class Promo(CustomBaseModel):
    active = models.BooleanField('Active?', default=False)
    name = models.CharField('Name', max_length=254, unique=True)
    slug = models.SlugField(max_length=254, null=True, blank=True)
    start_date = models.DateTimeField('Start From', null=True, default=default_start_datetime)
    end_date = models.DateTimeField('End On', null=True, default=default_end_datetime)
    apply_to_game = models.ManyToManyField(Game, related_name="gameset", blank=True)
    apply_to_dlc = models.ManyToManyField(DLC, related_name="dlcset", blank=True)
    landing_page = models.BooleanField('Landing Page?', default=False)
    media = models.ForeignKey(Media, null=True, blank=True, on_delete=models.SET_NULL)
    url = models.URLField('URL', max_length=1024, null=True, blank=True)
    is_featured = models.BooleanField('Add to Featured List', default=False, null=True, blank=True)
    carousel = models.BooleanField('Add to Home Carousel', default=False, null=True, blank=True)
    short_description = models.TextField(max_length=512, null=True, blank=True)
    long_description = models.TextField(max_length=1024, null=True, blank=True)


    def __str__(self) -> str:
        return self.name


    def clean(self):
        # Check if end date is before start date
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(
                "End date cannot be before start date.",
                code="invalid",
                params={"end_date": "End date"},
            )


    def save(self, *args, **kwargs):
        # Self contains no information about its fields, query the database instead.
        if self.landing_page and self.media is None:
            self.media = Media.objects.get(slug="no-image-landing")
        super().save(*args, **kwargs)
        promo = Promo.objects.get(id=self.id)
        if self.active and self.id is not None:
            for queryset in [promo.apply_to_game.all(), promo.apply_to_dlc.all()]:
                for game in queryset:
                    game.in_promo = True
                    game.promo = self
                    game.final_price = Decimal(
                        round(
                            game.base_price
                            * (1 + (Decimal(game.promo_percentage) / 100 * -1)),
                            2,
                        )
                    )
                    game.save()
        elif not self.active and self.id is not None:
            for queryset in [promo.apply_to_game.all(), promo.apply_to_dlc.all()]:
                for game in queryset:
                    game.in_promo = False
                    game.promo = None
                    game.promo_percentage = 0
                    game.final_price = game.base_price
                    game.save()


    def delete(self, using=None, keep_parents=False):
        remove_discount(self)
        return super().delete(using=using, keep_parents=keep_parents)


    pre_add = None
    post_add = None
    pre_remove = None
    post_remove = None

    # Manage status on adding/removing from M2M field.
    def _update_promo_items(self, **kwargs):
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
                    game.final_price = game.base_price
                    game.save()
            case 'pre_add':
                self.pre_add = set(self.apply_to_game.all())
                self.pre_add = self.pre_add.union(set(self.apply_to_dlc.all()))
            case 'post_add':
                self.post_add = set(self.apply_to_game.all())
                self.post_add = self.post_add.union(set(self.apply_to_dlc.all()))
                for i in self.post_add.difference(self.pre_add):
                    game = get_or_none(kwargs['model'], id=i.id)
                    if check_dupe(self, game):
                        break
                    game.in_promo = True if self.active else False
                    game.promo = self if self.active else None
                    game.save()
            case _:
                return
    
    def total_in_promo(self):
        return len(self.apply_to_game.all()) + len(self.apply_to_dlc.all())

    total_in_promo.short_description = "Games In Promo"

    def max_promo_percentage(self):
        promo_games = (
            self.apply_to_game.all()
            .aggregate(Max("promo_percentage"))
            .get("promo_percentage__max", 0)
        )
        promo_dlc = (
            self.apply_to_dlc.all()
            .aggregate(Max("promo_percentage"))
            .get("promo_percentage__max", 0)
        )
        highest_promo_percentage = max(
            promo_games if promo_games is not None else 0,
            promo_dlc if promo_dlc is not None else 0,
        )
        return highest_promo_percentage


# Controls actions that occur when a Promo becomes active/offline.
@receiver(pre_save, sender=Promo)
def promo_price_apply(instance, *args, **kwargs):
    promo = get_or_none(Promo, id=instance.id)
    if promo is not None:
        current = promo.active
        updated = instance.active
        apply_discount(instance) if current < updated else remove_discount(
            instance
        ) if current > updated else None


# Applies the discount to all associated games/DLCs when a Promo becomes active.
# It calculates the final price and sets the promo and in_promo fields for each game/DLC.
def apply_discount(instance):
    for queryset in [instance.apply_to_game.all(), instance.apply_to_dlc.all()]:
        for item in queryset:
            final_price = Decimal(
                round(
                    item.base_price * (1 + (Decimal(item.promo_percentage) / 100 * -1)),
                    2,
                )
            )
            queryset.filter(id=item.id).update(
                final_price=final_price, promo=instance, in_promo=True
            )


# Removes the discount from all associated games/DLCs when a Promo becomes offline.
# It sets the final price back to the base price and clears the promo and in_promo fields for each game/DLC.
def remove_discount(instance):
    for queryset in [instance.apply_to_game.all(), instance.apply_to_dlc.all()]:
        for item in queryset:
            final_price = item.base_price
            queryset.filter(id=item.id).update(
                final_price=final_price, promo_percentage=0, in_promo=False, promo=None
            )


@receiver(m2m_changed, sender=Promo.apply_to_game.through)
def game_change(instance, *args, **kwargs):
    instance._update_promo_items(**kwargs)


@receiver(m2m_changed, sender=Promo.apply_to_dlc.through)
def dlc_change(instance, *args, **kwargs):
    instance._update_promo_items(**kwargs)


def check_dupe(instance, game):
    """If the game passed in is already in another Promo - remove it from this Promo"""
    game_dupes = Promo.objects.filter(apply_to_game__id=game.id).exclude(id=instance.id)
    if len(game_dupes) > 0:
        if game.model_name() == "game":
            instance.apply_to_game.remove(game)
        else:
            instance.apply_to_dlc.remove(game)
