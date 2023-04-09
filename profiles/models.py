from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_countries.fields import CountryField


# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_phone_number = models.CharField(max_length=20, null=True, blank=True)
    default_street_address1 = models.CharField(max_length=20, null=True, blank=True)
    default_street_address2 = models.CharField(max_length=20, null=True, blank=True)
    default_town_or_city = models.CharField(max_length=20, null=True, blank=True)
    default_postcode = models.CharField(max_length=20, null=True, blank=True)
    default_country = CountryField(blank_label='Country*')
    default_county = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.user.username
    

@receiver(post_save, sender=User)
def get_or_add(sender, instance, **kwargs):
    """ If there is one, get it, if not create it """
    return UserProfile.objects.get_or_create(user=instance)