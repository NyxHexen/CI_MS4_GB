# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# Local
from .models import UserProfile
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@receiver(post_save, sender=User)
def get_or_add(sender, instance, **kwargs):
    """ If there is one, get it, if not create it """
    return UserProfile.objects.get_or_create(user=instance)