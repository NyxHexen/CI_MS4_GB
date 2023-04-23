# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

# Local
from .models import Media

# Internal
from games.models import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class MediaModelTest(TestCase):
    def setUp(self):
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
        self.assertIn(
            "Super Secret Page of Awesomeness!",
            f'{str(messages[0]).strip()}',
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
        self.assertIn(
            "Super Secret Page of Awesomeness!",
            f'{str(messages[0]).strip()}',
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
        self.assertIn(
            "Super Secret Page of Awesomeness!",
            f'{str(messages[0]).strip()}',
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
        self.assertRedirects(
            response,
            "/accounts/login/?next=/media/1/delete/"
            )

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
        self.assertIn(
            "Super Secret Page of Awesomeness!",
            f'{str(messages[0]).strip()}',
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
