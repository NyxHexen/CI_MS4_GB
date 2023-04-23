# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

# Local
from .models import *

# Third-party
from decimal import Decimal
from datetime import date
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class TestGamesViews(TestCase):
    def setUp(self):
        self.games_url = reverse('games')
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
        self.genre_1 = Genre.objects.create(name='RPG', slug='rpg')
        self.genre_2 = Genre.objects.create(name='Shooter', slug='shooter')
        self.tag = Tag.objects.create(name='First Person')
        self.feature = Feature.objects.create(name='Open World')
        self.developer = Developer.objects.create(
            name="Test Dev 1",
            country='GB'
        )
        self.publisher = Publisher.objects.create(
            name="Test Pub 1",
            country='GB',
        )
        self.platform = Platform.objects.create(
            name="PC",
            country='GB'
        )
        self.game = Game.objects.create(
            name="Assassin's Creed",
            description="An action-adventure game",
            storyline="A story about assassins",
            release_date=date(2007, 11, 13),
            base_price=round(Decimal(49.99), 2),
        )
        self.dlc = DLC.objects.create(
            required_game=self.game,
            name="Bassassin's Creed DLC",
            description="An action-adventure game DLC",
            storyline="A story about assassins DLC",
            release_date=date(2011, 5, 13),
            base_price=round(Decimal(49.99), 2),
        )
        self.game.genres.add(self.genre_1)
        self.dlc.genres.add(self.genre_2)
        self.rating_set = RatingSet.objects.create(
            game=self.game,
            dlc=None,
        )
        self.rating_set = RatingSet.objects.create(
            game=None,
            dlc=self.dlc,
        )
        self.esrb_rating = EsrbRating.objects.create(
            name="Teen",
        )
        self.pegi_rating = PegiRating.objects.create(
            name="17",
        )

    def test_games_view_db_query_exception(self):
        Game.objects.all().delete()
        DLC.objects.all().delete()
        response = self.client.get(self.games_url)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            f'{messages[0]}',
            "System Malfunction! Please try again later!"
        )

    def test_games_view_db_query_no_exception(self):
        response = self.client.get(self.games_url)
        self.assertEqual(response.status_code, 200)

    def test_games_view_filter(self):
        response_1 = self.client.get(self.games_url, data={'filter': 'on'})
        self.assertTrue('filter_dict' in response_1.context)

        response_2 = self.client.get(self.games_url, data={'filter': 'on', 'hide_extras': 'on'})
        self.assertEqual(len(response_2.context['page'].object_list), 1)

        response_3 = self.client.get("/games/?filter=true&genres_filter=shooter")
        self.assertEqual(len(response_3.context['page'].object_list), 1)
        self.assertEqual(response_3.context['page'].object_list, [self.dlc,])

    def test_games_view_sorting(self):
        response = self.client.get(self.games_url, data={'sort_by': 'title_desc'})
        self.assertEqual(response.context['page'].object_list[0], self.dlc)

    def test_games_view_pagination(self):
        response = self.client.get(self.games_url)
        self.assertEqual(len(response.context['page'].object_list), 2)

    def test_game_view_bad_game_id(self):
        response = self.client.get(reverse('game', kwargs={'model_name': 'game', 'game_id': '3'}))
        self.assertEqual(response.status_code, 404)

    def test_game_view_guest(self):
        response = self.client.get(reverse('game', kwargs={'model_name': 'game', 'game_id': '1'}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('media', response.context)
        self.assertIn('rating_count', response.context)
        self.assertEqual(list(response.context['media']), [])
        self.assertEqual(response.context['rating_count'], 0)
        self.assertNotIn('user_rating', response.context)

    def test_game_view_user(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        response = self.client.get(reverse('game', kwargs={'model_name': 'dlc', 'game_id': '1'}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('media', response.context)
        self.assertIn('rating_count', response.context)
        self.assertEqual(list(response.context['media']), [])
        self.assertEqual(response.context['rating_count'], 0)
        self.assertIn('user_rating', response.context)

    def test_set_game_rating_view_guest(self):
        url = reverse('set_game_rating', kwargs={
            'model_name': 'dlc',
            'game_id': f'{self.dlc.id}'}
            )
        response = self.client.post(url, content_type='application/json')
        self.assertEqual(response.json(), {'error': 'guest'})

    def test_game_view_bad_game_id_user(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('set_game_rating', kwargs={
            'model_name': 'game',
            'game_id': '5'}
            )
        response = self.client.post(url, content_type='application/json',
                                    data={'rating': '5'})
        self.assertEqual(response.status_code, 500)

    def test_set_game_rating_view_user(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('set_game_rating', kwargs={
            'model_name': 'dlc',
            'game_id': f'{self.dlc.id}'}
            )
        response = self.client.post(url, content_type='application/json',
                                    data={'rating': '5'})
        self.assertEqual(response.json(), {'new_game_rating': self.dlc.ratingset.user_rating_calc(), 'error': ''})

    def test_game_add_view_guest(self):
        url = reverse('game_add', kwargs={
            'model_name': 'game',
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/games/add/game")

    def test_game_add_view_non_staff(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('game_add', kwargs={
            'model_name': 'game',
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(
            "Super Secret Page of Awesomeness!",
            f'{str(messages[0]).strip()}',
        )

    def test_game_add_view_staff(self):
        self.client.login(
            username='test-super-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('game_add', kwargs={
            'model_name': 'game',
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            'name': 'GameForm Test',
            'description': 'Test Description',
            'storyline': 'Test Storyline',
            'genres': [self.genre_1.id,],
            'publishers': [self.publisher.id,],
            'developers': [self.developer.id,],
            'release_date': date(2007, 5, 13),
            'platforms': [self.platform.id,],
            'tags': [self.tag.id,],
            'features': [self.feature.id,],
            'media': [self.media_1.id, self.media_2.id,],
            'is_featured': True,
            'carousel': True,
            'base_price': round(Decimal(49.99), 2),
            'esrb_rating': self.esrb_rating.id,
            'pegi_rating': self.pegi_rating.id,
        }

        response = self.client.post(url, data=form_data)
        self.assertRedirects(response, "/games/game/2/")
        self.assertTrue(Game.objects.get(name=form_data['name']))

    def test_game_edit_view_guest(self):
        url = reverse('game_edit', kwargs={
            'model_name': 'game',
            'game_id': '1'
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/games/game/1/edit")

    def test_game_edit_view_non_staff(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('game_edit', kwargs={
            'model_name': 'game',
            'game_id': '1'
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            f'{str(messages[0]).strip()}',
            "Super Secret Page of Awesomeness! Unauthorized access prohibited!"
        )

    def test_game_edit_view_staff(self):
        self.client.login(
            username='test-super-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('game_edit', kwargs={
            'model_name': 'game',
            'game_id': '1'
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            'name': 'GameForm Test EDIT',
            'description': 'Test Description',
            'storyline': 'Test Storyline',
            'genres': [self.genre_1.id,],
            'publishers': [self.publisher.id,],
            'developers': [self.developer.id,],
            'release_date': date(2007, 5, 13),
            'platforms': [self.platform.id,],
            'tags': [self.tag.id,],
            'features': [self.feature.id,],
            'media': [self.media_1.id, self.media_2.id,],
            'is_featured': False,
            'carousel': False,
            'base_price': round(Decimal(33.99), 2),
            'esrb_rating': self.esrb_rating.id,
            'pegi_rating': self.pegi_rating.id,
        }

        response = self.client.post(url, data=form_data)
        self.assertRedirects(response, "/games/game/1/")
        self.assertTrue(Game.objects.get(name=form_data['name']))

    def test_game_delete_view_guest(self):
        url = reverse('game_delete', kwargs={
            'model_name': 'game',
            'game_id': '1'
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/games/game/1/delete/")
    
    def test_game_delete_view_non_staff(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('game_delete', kwargs={
            'model_name': 'game',
            'game_id': '2'
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(
            "Super Secret Page of Awesomeness!",
            f'{str(messages[0]).strip()}',
        )

    def test_game_delete_view_staff(self):
        self.client.login(
            username='test-super-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('game_delete', kwargs={
            'model_name': 'game',
            'game_id': '1'
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Game.objects.filter(id=1).exists())

    def test_game_attrs_view_bad_id(self):
        url = "/games/publishers/5/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            f'{str(messages[0]).strip()}',
            "System Malfunction! Please try again later!"
        )

        url = "/games/developers/7/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            f'{str(messages[0]).strip()}',
            "System Malfunction! Please try again later!"
        )

        url = "/games/platforms/9/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            f'{str(messages[0]).strip()}',
            "System Malfunction! Please try again later!"
        )

    def test_game_attrs_view(self):
        url = "/games/publishers/1/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = "/games/developers/1/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = "/games/platforms/1/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_game_attrs_view_sort(self):
        self.dlc.publishers.add(self.publisher)
        url="/games/publishers/1/?filter=true&sort_by=title_desc"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'].object_list[0], self.dlc)
        self.assertIn('filter_dict', response.context)


