# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

# Internal
from games.models import Game, DLC
from home.models import Media

# Local
from .models import Promo

# Included
from decimal import Decimal
from datetime import date, timedelta
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class PromoViewsTests(TestCase):
    def setUp(self):
        self.start_date = timezone.now().replace(
            microsecond=0,
            second=0
            )
        self.end_date = timezone.now().replace(
            microsecond=0,
            second=0
            ) + timedelta(days=1)
        self.user = User.objects.create_user(
            username='test-gamebox',
            password='gamebox-pwd',
            first_name="Test",
            last_name="Test",
            email="test@test.com",
            )
        self.super_user = User.objects.create_superuser(
            username='test-super-gamebox',
            password='gamebox-pwd',
            first_name="Test",
            last_name="Test",
            email="test@test.com"
            )
        self.media_1 = Media.objects.create(
            name='No Image LANDING',
            description='No Image LANDING',
            media_type='image',
        )
        self.media_2 = Media.objects.create(
            name='No Image COVER',
            description='No Image COVER',
            media_type='image'
        )
        self.game_1 = Game.objects.create(
            name="Assassin's Creed",
            description="An action-adventure game",
            storyline="A story about assassins",
            release_date=date(2007, 11, 13),
            base_price=round(Decimal(49.99), 2),
        )
        self.game_2 = Game.objects.create(
            name="Creed's Assassin",
            description="An adventure-action game",
            storyline="A story about Creed",
            release_date=date(2012, 11, 13),
            base_price=round(Decimal(29.99), 2),
        )
        self.dlc_1 = DLC.objects.create(
            required_game=self.game_1,
            name="Bassassin's Creed DLC",
            description="An action-adventure game DLC",
            storyline="A story about assassins DLC",
            release_date=date(2011, 5, 13),
            base_price=round(Decimal(19.99), 2),
        )
        self.dlc_2 = DLC.objects.create(
            required_game=self.game_2,
            name="Greed's Bassassin DLC",
            description="An action-horror game DLC",
            storyline="A story about bad assassins DLC",
            release_date=date(2011, 9, 12),
            base_price=round(Decimal(39.99), 2),
        )
        self.promo = Promo.objects.create(
            active=True,
            name="TEST PROMO 1",
            landing_page=True,
            is_featured=False,
            carousel=False,
            short_description="TEST",
            long_description="TESTTESTTEST",
        )
        self.promo.apply_to_game.add(self.game_1)
        self.promo.apply_to_game.add(self.game_2)

    def test_promo_view_inactive_guest(self):
        url = reverse('promo', kwargs={
            'promo_id': self.promo.id,
        })
        self.promo.active = False
        self.promo.save()
        response = self.client.get(url)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(
            "The Sale you are looking for is not currently available!",
            f'{messages[0]}',
        )

    def test_promo_view_inactive_staff(self):
        self.client.login(
            username='test-super-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('promo', kwargs={
            'promo_id': self.promo.id,
        })
        self.promo.active = False
        self.promo.save()
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_promo_view_sort(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('promo', kwargs={
            'promo_id': self.promo.id,
        })
        response = self.client.get(url, data={
            'sort_by': 'title_desc',
        })
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.context['page'].object_list[0], self.game_2)