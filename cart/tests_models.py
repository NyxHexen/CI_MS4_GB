# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Python
from decimal import Decimal

# Local
from .models import Cart, CartItem, Game, DLC
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class CartTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test-gamebox",
            password="gamebox-pwd"
        )
        self.cart = Cart.objects.create(
            user=self.user
        )

    def test_cart_created(self):
        self.assertEqual(self.cart.user.username, "test-gamebox")
        self.assertEqual(self.cart.total_in_cart(), Decimal(0.00))

    def test_cart_string_representation(self):
        self.assertEqual(str(self.cart), "test-gamebox")


class CartItemTestCase(TestCase):
    """
    A class for testing /checkout/ views.
    """

    def setUp(self):
        """
        Setup test game, user, and cartitems
        which will be used to test.
        """
        self.user = User.objects.create_user(
            username="test-gamebox",
            password="gamebox-pwd"
        )
        self.cart = Cart.objects.create(
            user=self.user
        )
        self.game = Game.objects.create(
            name="Test Game",
            base_price=round(Decimal(12.34), 2)
        )
        self.cart_item = CartItem.objects.create(
            cart=self.cart, 
            game=self.game, 
            quantity=2, 
            price=round(Decimal(24.68), 2)
        )

    def tearDown(self):
        """
        Delete test user, cart, game and dlc
        """
        User.objects.all().delete()
        Cart.objects.all().delete()
        Game.objects.all().delete()
        DLC.objects.all().delete()

    def test_cart_item_created(self):
        """
        Test items in the cart were correctly created.
        """
        self.assertEqual(self.cart_item.cart.user.username, "test-gamebox")
        self.assertEqual(self.cart_item.game.name, "Test Game")
        self.assertEqual(self.cart_item.quantity, 2)
        self.assertEqual(self.cart_item.price, round(Decimal(24.68),2))

    def test_clean_method(self):
        """
        Test that OrderItem's clean method works.
        """
        game = Game.objects.create(
            name="Test Game 2",
            base_price=Decimal(12.34)
        )
        dlc = DLC.objects.create(
            name="Test DLC",
            required_game=game,
            base_price=Decimal(12.34)
        )

        # Test that CartItem raises a ValidationError if neither game nor dlc is specified.
        cart_item = CartItem(
            cart=self.cart_item.cart,
            quantity=1,
            price=Decimal(12.34)
        )
        with self.assertRaises(ValidationError):
            cart_item.clean()

        # Test that CartItem can be saved if either game or dlc is specified.
        cart_item.game = game
        cart_item.dlc = None
        cart_item.clean()

        cart_item.game = None
        cart_item.dlc = dlc
        cart_item.clean()

        # Test that CartItem raises a ValidationError if both game and dlc are specified.
        cart_item.game = game
        cart_item.dlc = dlc
        with self.assertRaises(ValidationError):
            cart_item.clean()
        
        
