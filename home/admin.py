# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.contrib import admin

# Local
from .models import Media
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MediaAdmin(admin.ModelAdmin):
    """
    ModelAdmin class for Media model
    """
    list_display = (
        'name',
        'media_type',
        'media_use',
        'description'
    )

# Register your models here.
admin.site.register(Media, MediaAdmin)
