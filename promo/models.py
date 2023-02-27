from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from games.models import Game

from games.models import CustomBaseModel


class Promo(CustomBaseModel):
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, null=True, blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(auto_now_add=True)
    apply_to = models.ManyToManyField('games.Game', 'games.DLC+')
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
                self.pre_remove = set(self.apply_to.all())
            case 'post_remove':
                self.post_remove = set(self.apply_to.all())
                for i in self.pre_remove.difference(self.post_remove):
                    game = Game.objects.get(id=i.id)
                    game.in_promo = False
                    game.save()
            case 'pre_add':
                self.pre_add = set(self.apply_to.all())
            case 'post_add':
                self.post_add = set(self.apply_to.all())
                for i in self.post_add.difference(self.pre_add):
                    game = Game.objects.get(id=i.id)
                    game.in_promo = True
                    game.save()

    def delete(self, using=None, keep_parents=False):
        for i in self.apply_to.all():
                print(i.name)
                game = Game.objects.get(id=i.id)
                game.in_promo = False
                game.save()
        return super().delete(using=using, 
                              keep_parents=keep_parents)

    

@receiver(m2m_changed, sender=Promo.apply_to.through)
def receiver(instance, *args, **kwargs):
    instance._update_games(**kwargs)
    