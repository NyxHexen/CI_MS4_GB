from django.test import TestCase
from django.contrib.auth.models import User

from .forms import BillingAddressForm, NewsletterForm
from .models import UserProfile


class ProfilesFormsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test-gamebox', 
            password='gamebox-pwd',
            first_name="Test",
            last_name="Test",
            email="test@test.com"
            )
        self.form_data = {
            'user': self.user,
            'default_phone_number': '0123456789',
            'default_street_address1': '1 Test Road',
            'default_town_or_city': 'Cardiff',
            'default_postcode': '12345',
            'default_country': 'GB',
        }
        
    def test_form_valid_data(self):
        form = BillingAddressForm(self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_form_data(self):
        form_data = {
            'subscription_email': 'correct@example.com',
        }
        form = NewsletterForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['subscription_email'], 'correct@example.com')

    def test_form_bad_data(self):
        form_data = {
            'subscription_email': 'incorrectexamplecom',
        }
        form = NewsletterForm(data=form_data)
        self.assertFalse(form.is_valid())
