from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Sum

from games.models import Game, DLC


# Create your models here.
class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        unique=True
        )
    created_date = models.DateTimeField(
        default=timezone.now,
        )
    updated_date = models.DateTimeField(
        auto_now=True,
        )

    def __str__(self):
        return self.user.username
    
    def total_in_cart(self):
        """
        Calculate the total value of all items in the cart.

        Returns:
            float: The total value of all items in the cart.
        """
        if self.cartitems.count() > 0:
            return round(
                self.cartitems.aggregate(
                Sum('price')
                )['price__sum'], 2
                )
        else:
            return 0.00

    total_in_cart.short_description = "Cart Total"

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='cartitems'
        )
    game = models.ForeignKey(
        Game,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        )
    dlc = models.ForeignKey(
        DLC,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        )
    quantity = models.PositiveIntegerField(
        default=1,
        )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2
        )

    def clean(self):
        """
        Ensure that either a game or a DLC is specified, but not both, and not neither.

        Returns:
            dict: The cleaned data.
        Raises:
            ValidationError: If neither a game nor a DLC is specified, or if both a game and a DLC are specified.
        """
        if not self.game and not self.dlc:
            raise ValidationError("Either game or dlc must be specified.")
        if self.game and self.dlc:
            raise ValidationError("Only one of game or dlc can be specified.")
        return super().clean()
    
    # https://stackoverflow.com/questions/1737017/django-auto-now-and-auto-now-add
    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        self.cart.updated_date = timezone.now()
        self.cart.save()
        return super().save(*args, **kwargs)
