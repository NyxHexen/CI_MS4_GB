# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.conf import settings

# Internal
from profiles.forms import NewsletterForm
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def newsletter_form(request):
    """
    Context processor making NewsletterForm
    available site-wise.
    """
    data = {
        "newsletter_form": NewsletterForm()
    }
    return data