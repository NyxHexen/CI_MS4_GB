# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User

# Third-party
from django_countries.fields import CountryField

# Local
from games.models import Game, DLC
import uuid
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        )
    order_number = models.CharField(
        max_length=32,
        null=False,
        editable=False,
        )
    full_name = models.CharField(
        max_length=50,
        )
    email = models.EmailField(
        max_length=254
        )
    phone_number = models.CharField(
        max_length=20
        )
    country = CountryField(
        blank_label='Country*'
        )
    postcode = models.CharField(
        max_length=20,
        null=True,
        blank=True
        )
    town_or_city = models.CharField(
        max_length=40
        )
    street_address1 = models.CharField(
        max_length=80
        )
    street_address2 = models.CharField(
        max_length=80,
        null=True,
        blank=True
        )
    county = models.CharField(
        max_length=80,
        null=True,
        blank=True
        )
    date = models.DateTimeField(
        auto_now_add=True
        )
    order_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
        )
    original_cart = models.TextField(
        default=''
        )
    stripe_pid = models.CharField(
        max_length=254,
        default=''
        )

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total each time a line item is added.
        """
        self.order_total = self.lineitems.aggregate(Sum('price'))['price__sum']
        self.save()

    def save(self, *args, **kwargs):
        """
        Override save method to ensure order_number is not empty.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='lineitems'
        )
    game = models.ForeignKey(
        Game,
        null=True,
        blank=True,
        on_delete=models.CASCADE
        )
    dlc = models.ForeignKey(
        DLC,
        null=True,
        blank=True,
        on_delete=models.CASCADE
        )
    quantity = models.PositiveIntegerField(
        default=1
        )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2
        )

    def save(self, *args, **kwargs):
        """
        Override save method to calculate and set the price of a CartItem
        instance before saving it to the database.
        """
        self.price = (
            self.game.final_price * self.quantity
            if self.game is not None
            else self.dlc.final_price * self.quantity
            )
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.order.order_number[:6]
