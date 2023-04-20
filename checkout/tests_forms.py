# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 3rd party:
from django.test import TestCase

# Internal:
from .forms import OrderForm

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class TestCheckoutForms(TestCase):
    """
    A class for testing checkout forms
    """
    def setUp(self):
        self.form_data = {
                "full_name": "Test Test",
                "email": "test@test.com",
                "phone_number": "0123456789",
                "country": "GB",
                "town_or_city": "Test City",
                "street_address1": "1 Test Road",
            }

    def test_add_order_form(self):
        """
        Test OrderForm functionality.
        """
        form = OrderForm(self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_validation(self):
        self.form_data.pop('country')
        form = OrderForm(self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("country", form.errors)


    