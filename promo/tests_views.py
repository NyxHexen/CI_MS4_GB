from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

from games.models import Game, DLC
from home.models import Media
from .models import Promo

from decimal import Decimal
from datetime import date, timedelta

class PromoViewsTests(TestCase):
    def setUp(self):
        self.start_date = timezone.now().replace(microsecond=0, second=0)
        self.end_date = timezone.now().replace(microsecond=0, second=0) + timedelta(days=1)
        self.user = User.objects.create_user(
            username='test-gamebox', 
            password='gamebox-pwd',
            first_name="Test",
            last_name="Test",
            email="test@test.com"
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

    def test_promo_add_view_guest(self):
        url = reverse('promo_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/promo/add/")

    def test_promo_add_view_non_staff(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('promo_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            f'{str(messages[0]).strip()}',
            "Super Secret Page of Awesomeness! Unauthorized access prohibited!"
        )

    def test_promo_add_view_staff_preview(self):
        self.client.login(
            username='test-super-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('promo_add')
        self.promo.apply_to_game.remove(self.game_1)
        response = self.client.post(url, data={
            'active': True,
            'name': "TEST PROMO",
            'start_date': self.start_date,
            'end_date': self.end_date,
            'landing_page': True,
            'is_featured': False,
            'carousel': False,
            'short_description': 'TEST',
            'long_description': 'TESTTESTTEST',
            'apply_to_game': [self.game_1.id, self.game_2.id],
            'submit_option': 'preview',
            f'game_discount-game_{self.game_1.id}': 30,
            f'game_discount-game_{self.game_2.id}': 40,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Promo.objects.filter(id=2).exists())
        self.assertEqual(response.context['real_game_list'], [self.game_1,])

    def test_promo_add_view_staff_save(self):
        self.client.login(
            username='test-super-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('promo_add')
        self.promo.apply_to_game.remove(self.game_2)
        response = self.client.post(url, data={
            'active': True,
            'name': "TEST PROMO 2",
            'landing_page': True,
            'start_date': f'{self.start_date}',
            'end_date': f'{self.end_date}',
            'is_featured': False,
            'carousel': False,
            'short_description': 'TEST',
            'long_description': 'TESTTESTTEST',
            'apply_to_game': [self.game_1.id, self.game_2.id],
            'submit_option': 'save',
            f'game_discount-game_{self.game_1.id}': 30,
            f'game_discount-game_{self.game_2.id}': 40,
        })
        promo = Promo.objects.filter(id=2)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(promo.exists())
        self.assertQuerysetEqual(promo[0].apply_to_game.all(), {self.game_2})

    def test_promo_edit_view_guest(self):
        url = reverse('promo_edit', kwargs={
            'promo_id': 1,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/promo/1/edit/")

    def test_promo_edit_view_non_staff(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('promo_edit', kwargs={
            'promo_id': 1,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            f'{str(messages[0]).strip()}',
            "Super Secret Page of Awesomeness! Unauthorized access prohibited!"
        )

    def test_promo_edit_view_staff_preview(self):
        self.client.login(
            username='test-super-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('promo_edit', kwargs={
            'promo_id': 1,
        })
        self.promo.apply_to_game.remove(self.game_1)
        self.promo.apply_to_game.remove(self.game_2)
        self.assertEqual(self.promo.apply_to_game.all().count(), 0)
        response = self.client.post(url, data={
            'active': True,
            'name': "TEST PROMO EDIT",
            'start_date': self.start_date,
            'end_date': self.end_date,
            'landing_page': True,
            'is_featured': False,
            'carousel': False,
            'short_description': 'TEST',
            'long_description': 'TESTTESTTEST',
            'apply_to_game': [self.game_2.id],
            'apply_to_dlc': [self.dlc_1.id],
            'submit_option': 'preview',
            f'game_discount-dlc_{self.dlc_1.id}': 30,
            f'game_discount-game_{self.game_2.id}': 40,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['game_list'], [self.game_2, self.dlc_1,])
        self.assertNotEqual(self.promo.name, "TEST PROMO EDIT")

    def test_promo_edit_view_staff_save(self):
        self.client.login(
            username='test-super-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('promo_edit', kwargs={
            'promo_id': 1,
        })
        self.promo.apply_to_game.remove(self.game_2)
        response = self.client.post(url, data={
            'active': True,
            'name': "TEST PROMO EDIT",
            'start_date': self.start_date,
            'end_date': self.end_date,
            'landing_page': True,
            'is_featured': False,
            'carousel': False,
            'short_description': 'TEST',
            'long_description': 'TESTTESTTEST',
            'apply_to_game': [self.game_2.id],
            'apply_to_dlc': [self.dlc_1.id],
            'submit_option': 'save',
            f'game_discount-dlc_{self.dlc_1.id}': 30,
            f'game_discount-game_{self.game_2.id}': 40,
        })
        self.assertEqual(response.status_code, 302)
        promo = Promo.objects.get(id=1)
        self.assertEqual(promo.name, "TEST PROMO EDIT")
        self.assertRedirects(response, reverse('promo', kwargs={
            'promo_id': 1,
        }))

    def test_promo_edit_view_staff_save(self):
        self.client.login(
            username='test-super-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('promo_edit', kwargs={
            'promo_id': 1,
        })
        self.promo.apply_to_game.remove(self.game_2)
        response = self.client.post(url, data={
            'active': False,
            'name': "TEST PROMO EDIT",
            'start_date': self.start_date,
            'end_date': self.end_date,
            'landing_page': True,
            'is_featured': False,
            'carousel': False,
            'short_description': 'TEST',
            'long_description': 'TESTTESTTEST',
            'apply_to_game': [self.game_2.id],
            'apply_to_dlc': [self.dlc_1.id],
            'submit_option': 'activate',
            f'game_discount-dlc_{self.dlc_1.id}': 30,
            f'game_discount-game_{self.game_2.id}': 40,
        })
        self.assertEqual(response.status_code, 302)
        promo = Promo.objects.get(id=1)
        self.assertEqual(promo.active, True)
        self.assertRedirects(response, reverse('promo', kwargs={
            'promo_id': 1,
        }))

    def test_promo_delete_view_guest(self):
        url = reverse('promo_delete', kwargs={
            'promo_id': 1,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/promo/1/delete/")

    def test_promo_delete_view_non_staff(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('promo_delete', kwargs={
            'promo_id': 1,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            f'{str(messages[0]).strip()}',
            "Super Secret Page of Awesomeness! Unauthorized access prohibited!"
        )

    def test_promo_delete_view_staff_invalid(self):
        self.client.login(
            username='test-super-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('promo_delete', kwargs={
            'promo_id': 3,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            f'{str(messages[0]).strip()}',
            "Promo matching query does not exist."
        )

    def test_promo_delete_view_staff_valid(self):
        self.client.login(
            username='test-super-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('promo_delete', kwargs={
            'promo_id': 1,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Promo.objects.filter(id=1).exists())
