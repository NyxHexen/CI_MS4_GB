# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.contrib import admin

# Local
from .models import UserProfile
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class UserProfileAdmin(admin.ModelAdmin):
    """
    ModelAdmin class for UserProfile model
    """
    list_display = (
        'user',
        'newsletter_sub',
        'default_postcode',
        'default_country'
    )


admin.site.register(UserProfile, UserProfileAdmin)
