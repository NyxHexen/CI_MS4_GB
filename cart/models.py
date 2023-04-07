from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

from games.models import Game, DLC


# Create your models here.
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cartitems')
    game = models.ForeignKey(Game, null=True, blank=True, on_delete=models.CASCADE)
    dlc = models.ForeignKey(DLC, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def clean(self):
        if not self.game and not self.dlc:
            raise ValidationError("Either game or dlc must be specified.")
        if self.game and self.dlc:
            raise ValidationError("Only one of game or dlc can be specified.")
        return super().clean()
