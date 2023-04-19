from django.db import models
from django.db.models import Max
from django.core.exceptions import ValidationError
from decimal import Decimal

from games.models import CustomBaseModel, DLC, Game
from home.models import Media
from ci_ms4_gamebox.utils import get_or_none
from .utils import (default_start_datetime, default_end_datetime,
                    remove_discount)


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
                    if self.check_dupe(self, game):
                        break
                    game.in_promo = True if self.active else False
                    game.promo = self if self.active else None
                    game.save()
            case _:
                return
            

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
    
    
    @staticmethod
    def check_dupe(instance, game):
        """If the game passed in is already in another Promo - remove it from this Promo"""
        game_dupes = Promo.objects.filter(apply_to_game__id=game.id).exclude(id=instance.id)
        if len(game_dupes) > 0:
            if game.model_name() == "game":
                instance.apply_to_game.remove(game)
            else:
                instance.apply_to_dlc.remove(game)


    def total_in_promo(self):
        return len(self.apply_to_game.all()) + len(self.apply_to_dlc.all())

    total_in_promo.short_description = "Games In Promo"
