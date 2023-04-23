# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.test import TestCase
from django.core.signing import Signer
from django.contrib.messages import get_messages
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal

# Third-party
import json

# Local
from .models import Order
from home.models import Media
from games.models import Game
from cart.models import Cart
from checkout.forms import OrderForm
from profiles.models import UserProfile

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class TestCheckoutViews(TestCase):
    """
    A class for testing checkout views
    """
    def setUp(self):
        self.signer = Signer()
        self.user = User.objects.create_user(
            username='test-gamebox',
            password='gamebox-pwd',
            first_name="Test",
            last_name="Test",
            email="test@test.com"
            )

        self.user.userprofile.default_phone_number = "0123456789"
        self.user.userprofile.default_street_address1 = "Test Address 1"
        self.user.userprofile.default_street_address2 = "Test Address 2"
        self.user.userprofile.default_town_or_city = "Test City"
        self.user.userprofile.default_postcode = "12345"
        self.user.userprofile.default_country = "GB"
        self.user.userprofile.default_county = ""
        self.user.userprofile.save()

        self.cart = Cart.objects.create(
            user=self.user
            )

        self.order = Order.objects.create(
            user=self.user,
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

        Media.objects.create(
            name='No Image LANDING',
            description='No Image LANDING',
            media_type='image'
        )

        Media.objects.create(
            name='No Image COVER',
            description='No Image COVER',
            media_type='image'
        )

        self.user.userprofile.default_phone_number = '0123456789'
        self.user.userprofile.default_country = 'GB'
        self.user.userprofile.default_town_or_city = 'Test City'
        self.user.userprofile.default_street_address1 = 'Test Street 1'

    def tearDown(self):
        User.objects.all().delete()
        Cart.objects.all().delete()
        UserProfile.objects.all().delete()

    def test_empty_cart_checkout_guest(self):
        url = reverse('checkout')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('cart'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            f'{messages[0]}',
            "You cannot checkout with an empty cart!"
        )

    def test_empty_cart_checkout_user(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('checkout')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('cart'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            f'{messages[0]}',
            "You cannot checkout with an empty cart!"
        )

    def test_checkout_guest(self):
        url = reverse('checkout')
        add_item_url = reverse('cart_add', kwargs={
            'model_name': 'game',
            'game_id': f'{self.game.id}'}
            )
        self.client.post(add_item_url,
                         {'quantity': 1, 'redirect_url': '/games/'})
        response = self.client.get(url)
        self.assertIsInstance(response.context['order_form'], OrderForm)

    def test_checkout_user(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('checkout')
        self.cart.cartitems.create(
            game_id=1,
            quantity=2,
            price=round(Decimal(19.98), 2))
        response = self.client.get(url)
        self.assertIsInstance(response.context['order_form'], OrderForm)

    def test_checkout_success(self):
        order = Order.objects.create(user=self.user)
        url = reverse('checkout_success',
                      kwargs={'order_number': order.order_number})
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd',
            )

        response = self.client.get(url)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(
            f"Order successfully processed!",
            f'{messages[0]}',
        )
        self.assertEqual(response.context['order'], order)

    def test_cart_deleted_guest(self):
        order = Order.objects.create(user=self.user)
        url = reverse('checkout_success',
                      kwargs={'order_number': order.order_number})
        session_cart = self.client.session.get('cart', {})
        session_cart[f'{self.game.id}'] = {
            'model': self.game.model_name(),
            'quantity': 1
        }
        cart = json.dumps(session_cart)
        signer = Signer()
        cart_signed = signer.sign(cart)
        self.client.session['cart'] = {'cart_signed': cart_signed}
        response = self.client.get(url)
        session_cart = self.client.session.get('cart', {})
        self.assertDictEqual(session_cart, {})

    def test_cart_deleted_user(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )

        self.cart.cartitems.create(
            game_id=1,
            quantity=2,
            price=round(Decimal(19.98), 2)
            )
        url = reverse('checkout_success',
                      kwargs={'order_number': self.order.order_number})
        response = self.client.get(url)
        with self.assertRaises(Cart.DoesNotExist):
            self.cart.refresh_from_db()

    def test_post_method_guest(self):
        form_data = {
            "full_name": "Test Test",
            "email": "test@test.com",
            "phone_number": "0123456789",
            "country": "GR",
            "town_or_city": "Test City",
            "street_address1": "1 Test Road",
            "client_secret": "test_secret123"
        }
        add_item_url = reverse('cart_add', kwargs={
            'model_name': 'game',
            'game_id': f'{self.game.id}'}
            )
        response = self.client.post(
            add_item_url,
            {'quantity': 1, 'redirect_url': '/games/'}
            )
        self.client.post(
            reverse('checkout'),
            data=form_data
            )
        order = Order.objects.get(stripe_pid="test")
        self.assertNotEqual(
            self.user.userprofile.default_country,
            form_data.get('country')
            )
        self.assertIsNotNone(order.original_cart)
        self.assertNotEqual(order.lineitems.count(), 0)

    def test_post_method_user(self):
        form_data = {
            "save-info": 'on',
            "full_name": "Test Test",
            "email": "test@test.com",
            "phone_number": "0123456789",
            "country": "GR",
            "town_or_city": "Test City",
            "street_address1": "1 Test Road",
            "client_secret": "test_secret123"
        }
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        add_item_url = reverse('cart_add', kwargs={
            'model_name': 'game',
            'game_id': f'{self.game.id}'}
            )
        add_response = self.client.post(
            add_item_url,
            {'quantity': 1, 'redirect_url': '/games/'}
            )
        chk_response = self.client.post(reverse('checkout'), data=form_data)
        user = User.objects.get(username=self.user.username)
        order = Order.objects.get(stripe_pid="test")
        self.assertEqual(user.userprofile.default_country, 'GR')
        self.assertEqual(user.userprofile.default_country, order.country.code)
        self.assertIsNotNone(order.original_cart)
        self.assertNotEqual(order.lineitems.count(), 0)

    def test_create_stripe_intent_get(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )

        url = reverse('create_stripe_intent')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_create_stripe_intent_post(self):
        url = reverse('create_stripe_intent')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        add_item_url = reverse('cart_add', kwargs={
            'model_name': 'game',
            'game_id': f'{self.game.id}'}
            )
        add_response = self.client.post(
            add_item_url,
            {'quantity': 1, 'redirect_url': '/games/'}
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('client_secret', response.json())

    def test_modify_stripe_intent_get(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )

        url = reverse('modify_stripe_intent')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_modify_stripe_intent_post(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )

        url = reverse('create_stripe_intent')

        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)

        add_item_url = reverse('cart_add', kwargs={
            'model_name': 'game',
            'game_id': f'{self.game.id}'}
            )
        add_response = self.client.post(
            add_item_url,
            {'quantity': 1, 'redirect_url': '/games/'}
            )
        response = self.client.post(url)
        client_secret = response.json()["client_secret"]

        response = self.client.post(
            url,
            body={'client_secret': client_secret, 'save-info': True},
            content_type="application/json"
            )
        self.assertEqual(response.status_code, 200)
