# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django import forms
# Local
from .models import UserProfile
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class BillingAddressForm(forms.ModelForm):
    """
    ModelForm for BIlling Address collection.
    """
    class Meta:
        model = UserProfile
        fields = (
            "default_phone_number",
            "default_street_address1",
            "default_street_address2",
            "default_town_or_city",
            "default_postcode",
            "default_county",
            "default_country",
        )

    def __init__(self, *args, **kwargs):
        """
        Update label values and set autofocus on phone number.
        """
        super().__init__(*args, **kwargs)
        labels = {
            "default_phone_number": "Phone Number",
            "default_country": "Country",
            "default_postcode": "Postal Code",
            "default_town_or_city": "Town or City",
            "default_street_address1": "Street Address 1",
            "default_street_address2": "Street Address 2",
            "default_county": "County",
        }

        self.fields["default_phone_number"].widget.attrs["autofocus"] = True
        for field in self.fields:
            self.fields[field].label = labels[field]


class NewsletterForm(forms.Form):
    """
    ModelForm for newsletter subscription.
    """
    subscription_email = forms.EmailField(
        label='Email: *',
        max_length=320,
        required=True
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            'subscription_email'].widget.attrs["placeholder"] = 'Email Address'
        self.fields['subscription_email'].label = False
