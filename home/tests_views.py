from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

from decimal import Decimal
from datetime import date

from .models import Media
from games.models import *

class MediaModelTest(TestCase):
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

    def test_media_view_guest(self):
        url = reverse('media')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/media/")

    def test_media_view_non_staff(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('media')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            f'{str(messages[0]).strip()}',
            "Super Secret Page of Awesomeness! Unauthorized access prohibited!"
        )
    
    def test_media_view_staff(self):
        self.client.login(
            username='test-super-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('media')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('filtered_game_list', response.context)
        self.assertIn('unassigned_media', response.context)

    def test_media_add_view_guest(self):
        url = reverse('media_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/media/add/")

    def test_media_add_view_non_staff(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('media_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            f'{str(messages[0]).strip()}',
            "Super Secret Page of Awesomeness! Unauthorized access prohibited!"
        )

    def test_media_add_view_staff(self):
        self.client.login(
            username='test-super-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('media_add')
        response = self.client.post(url, data={
            'name': 'Test Media',
            'url': 'http://youtube.com/test-media/',
            'media_type': 'video',
            'media_use': 'PREVIEW',
            'description': 'This is a test media file ALT.',
        })
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(
            " has been saved successfully!",
            f'{str(messages[0]).strip()}',
        )

    def test_media_edit_view_guest(self):
        url = reverse('media_edit', kwargs={'media_id': '1'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/media/1/edit/")

    def test_media_edit_view_non_staff(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('media_edit', kwargs={'media_id': '1'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            f'{str(messages[0]).strip()}',
            "Super Secret Page of Awesomeness! Unauthorized access prohibited!"
        )
        
    def test_media_edit_view_staff(self):
        self.client.login(
            username='test-super-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('media_edit', kwargs={'media_id': '1'})
        response = self.client.post(url, data={
            'name': 'Test Media',
            'url': 'http://pinterest.com/test-media/',
            'media_type': 'video',
            'media_use': 'COVER',
            'description': 'ALT Game Edit Test.',
        })
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(
            " has been edited successfully!",
            f'{str(messages[0]).strip()}',
        )

    def test_media_delete_view_guest(self):
        url = reverse('media_delete', kwargs={'media_id': '1'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/media/1/delete/")

    def test_media_delete_view_non_staff(self):
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('media_delete', kwargs={'media_id': '1'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            f'{str(messages[0]).strip()}',
            "Super Secret Page of Awesomeness! Unauthorized access prohibited!"
        )

    def test_media_delete_view_staff(self):
        self.client.login(
            username='test-super-gamebox',
            password='gamebox-pwd'
            )
        url = reverse('media_delete', kwargs={'media_id': '1'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Media.objects.filter(id='1').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(
            " has been deleted successfully!",
            f'{str(messages[0]).strip()}',
        )

    def test_about_page_view(self):
        url = reverse('about')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'home/about.html')

    def test_support_page_view(self):
        url = reverse('support')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'home/support.html')