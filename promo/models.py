from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from games.models import Game, DLC
from games.models import CustomBaseModel
from ci_ms4_gamebox.utils import get_or_none


class Promo(CustomBaseModel):
    active = models.BooleanField(default=False)
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, null=True, blank=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    apply_to_game = models.ManyToManyField('games.Game', related_name='mtm')
    apply_to_dlc = models.ManyToManyField('games.DLC', related_name='mtm', blank=True)
    landing_page = models.BooleanField(default=False)
    url = models.URLField(max_length=1024, null=True, blank=True)

    def __str__(self) -> str:
        return self.name


    pre_add = None
    post_add = None
    pre_remove = None
    post_remove = None
    
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
