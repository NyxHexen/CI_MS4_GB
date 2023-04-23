# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal

# Third-party
import uuid

# Local
from games.models import Game
from checkout.models import Order, OrderLineItem
from profiles.models import UserProfile
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class TestOrderModel(TestCase):
    """
    A class for testing Order model.
    """
    def setUp(self):
        """
        Create test users and test order
        """
        self.test_user = User.objects.create_user(
            username='test-gamebox', password='gamebox-pwd'
        )
        self.test_user_profile = UserProfile.objects.get(user=self.test_user)
        self.order = Order.objects.create(
            user=self.test_user,
            full_name="Test User",
            email="info@example.com",
            phone_number="0123456789",
            country="GB",
            town_or_city="Test City",
            street_address1="Test Address 1",
        )

        self.game = Game.objects.create(
            name="Test Game",
            description="Test Description",
            storyline="Test Storyline",
            base_price=Decimal(9.99),
        )

    def tearDown(self):
        """
        Delete Test orders
        """
        Order.objects.all().delete()

    def test_method_order_number(self):
        self.assertEqual(
            len(self.order.order_number), len(uuid.uuid4().hex.upper())
            )

    def test_method_update_total(self):
        OrderLineItem.objects.create(
            order=self.order,
            game=self.game,
            dlc=None,
            quantity=2,
            price=Decimal(9.99),
        )
        self.assertEqual(self.order.order_total, round(Decimal(19.98), 2))
