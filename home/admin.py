from django.contrib import admin

from .models import Media

class MediaAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'media_type',
        'media_use',
        'description'
    )

# Register your models here.
admin.site.register(Media, MediaAdmin)
