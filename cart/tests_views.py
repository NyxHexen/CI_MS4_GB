from django.test import TestCase
from django.core.signing import Signer
from django.urls import reverse
from django.contrib.auth import get_user
from django.contrib.auth.models import User
from decimal import Decimal
from games.models import Game, DLC
from cart.models import Cart, CartItem

import json


class CartViewTests(TestCase):
    """
    A class for testing /checkout/ views.
    """

    def setUp(self):
        """
        Setup test client, signer, game, user, and cart
        which will be used to test.
        """
        self.signer = Signer()
        self.game = Game.objects.create(
            name='Test Game',
            base_price=Decimal('19.99')
            )
        self.user = User.objects.create_user(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        self.cart = Cart.objects.create(
            user=self.user
            )

    def tearDown(self):
        """
        Delete test user, cart, and game
        """
        User.objects.all().delete()
        Cart.objects.all().delete()
        Game.objects.all().delete()

    def test_cart_add_guest(self):
        """
        Test Guest User add to cart functionality.
        """
        url = reverse(
            'cart_add',
            kwargs={'model_name': 'game', 'game_id': self.game.id}
            )
        self.client.post(
            url,
            {'quantity': 1, 'redirect_url': '/games/'}
            )
        cart = self.client.session.get('cart')
        self.assertIsNotNone(cart)
        unsigned_cart = self.signer.unsign(cart['cart_signed'])
        loaded_cart = json.loads(unsigned_cart)
        self.assertIsNotNone(loaded_cart)
        self.assertEqual(loaded_cart[f'{self.game.id}']['model'], 'game')
        self.assertEqual(loaded_cart[f'{self.game.id}']['quantity'], 1)

    def test_cart_remove_guest(self):
        """
        Test Guest User remove from cart functionality.
        """
        add_item_url = reverse('cart_add', kwargs={
            'model_name': 'game',
            'game_id': f'{self.game.id}'}
            )
        self.client.post(add_item_url,
                         {'quantity': 1, 'redirect_url': '/games/'})
        del_item_url = reverse('cart_remove')
        del_response = self.client.post(
            del_item_url,
            content_type='application/json',
            data=json.dumps(
                {'game_id': f'{self.game.id}',
                    'model_name': 'game'}
                )
            )
        self.assertEqual(get_user(self.client).is_authenticated, False)
        self.assertEqual(del_response.json(), {'success': True})
        cart = self.client.session.get('cart')
        unsigned_cart = self.signer.unsign(cart['cart_signed'])
        loaded_cart = json.loads(unsigned_cart)
        self.assertNotIn(f'{self.game.id}', loaded_cart)

    def test_cart_add_user(self):
        """
        Test Registered User add to cart functionality.
        """
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd')
        url = reverse(
            'cart_add',
            kwargs={'model_name': 'game', 'game_id': self.game.id}
            )
        response = self.client.post(
            url,
            {'quantity': 1, 'redirect_url': '/games/'}
            )
        self.assertEqual(get_user(self.client).is_authenticated, True)
        cart_item = self.cart.cartitems.get(game=self.game)
        self.assertIsNotNone(cart_item)
        self.assertEqual(cart_item.quantity, 1)
        self.assertEqual(cart_item.price, self.game.final_price)
        self.client.post(
            url,
            {'quantity': 1, 'redirect_url': '/games/'}
            )
        cart_item = self.cart.cartitems.get(game=self.game)
        self.assertEqual(cart_item.quantity, 2)
        response = self.client.get('/')
        self.assertEqual(response.context['total'], self.game.final_price * 2)

        

    def test_cart_remove_user(self):
        """
        Test Registered User remove from cart functionality.
        """
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )

        cart_item = CartItem.objects.create(
            cart=self.cart,
            game=self.game,
            quantity=1,
            price=self.game.final_price
            )
        url = reverse('cart_remove')
        response = self.client.post(
            url,
            content_type='application/json',
            data={'game_id': self.game.id, 'model_name': 'game'}
            )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        self.assertFalse(CartItem.objects.filter(
            id=cart_item.id).exists()
            )
        self.assertEqual(self.cart.total_in_cart(), Decimal('0.00'))
