# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

# Internal
from home.models import Media
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class MediaModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test-gamebox', 
            password='gamebox-pwd',
            first_name="Test",
            last_name="Test",
            email="test@test.com"
            )
        Media.objects.create(
            name='No Image LANDING',
            description='No Image LANDING',
            media_type='image',
        )
        Media.objects.create(
            name='No Image COVER',
            description='No Image COVER',
            media_type='image'
        )
        
    def test_myprofile_view_unauth(self):
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/myprofile/')

    def test_myprofile_view_auth(self):
        url = reverse('profile')
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        response = self.client.post(url, data={
            'myprofile_first_name': "Profile",
            'myprofile_last_name': "Test",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile', response.context)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.first_name, "Profile")

    def test_billing_address_view_unauth(self):
        url = reverse('billing_address')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/myprofile/billing/')

    def test_billing_address_view_auth(self):
        url = reverse('billing_address')
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('user_profile', response.context)

        self.assertEqual(self.user.userprofile.default_phone_number, None)
        response = self.client.post(url, data={
            "default_phone_number": "9876543210",
            "default_country": "TR",
            "default_postcode": "11111",
            "default_town_or_city": "Swansea",
            "default_street_address1": "1 BillingTest Road",
            "default_street_address2": "BillingTest Close",
            "default_county": "South Glamorgan",
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.userprofile.default_phone_number, "9876543210")
        self.assertRedirects(response, '/myprofile/billing/')
    
    def test_newsletter_sub_unauth(self):
        url = reverse('newsletter_sub')
        response = self.client.post(url, data={
            'subscription_email': f"{self.user.email}",
            'newsletter_redirect': reverse('home'),
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_newsletter_sub_auth_new(self):
        url = reverse('newsletter_sub')
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        response = self.client.post(url, data={
            'subscription_email': f"{self.user.email}",
            'newsletter_redirect': reverse('home'),
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.userprofile.newsletter_sub)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(
            "Thank you for subscribing to our newsletter.",
            f'{str(messages[0]).strip()}',
        )

    def test_newsletter_sub_auth_existing(self):
        url = reverse('newsletter_sub')
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        self.user.userprofile.newsletter_sub = True
        self.user.userprofile.save()
        response = self.client.post(url, data={
            'subscription_email': f"{self.user.email}",
            'newsletter_redirect': reverse('home'),
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.userprofile.newsletter_sub)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(
            "You are already subscribed!",
            f'{str(messages[0]).strip()}',
        )

    def test_newsletter_sub_auth_unknown(self):
        url = reverse('newsletter_sub')
        self.client.login(
            username='test-gamebox',
            password='gamebox-pwd'
            )
        response = self.client.post(url, data={
            'subscription_email': "someother@email.com",
            'newsletter_redirect': reverse('home'),
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        user = User.objects.get(id=self.user.id)
        self.assertFalse(user.userprofile.newsletter_sub)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(
            "Newsletter can only be sent to your primary e-mail address.",
            f'{str(messages[0]).strip()}',
        )