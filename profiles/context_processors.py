from django.conf import settings
from profiles.forms import NewsletterForm

def newsletter_form(request):
    data = {
        "newsletter_form": NewsletterForm()
    }
    return data