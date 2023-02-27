from django.contrib import admin
from games.models import Game
from .models import *

# Register your models here.
class PromoAdmin(admin.ModelAdmin):
    filter_horizontal = ['apply_to',]
    list_display = ['id', 'name']
    readonly_fields = ['slug',]

admin.site.register(Promo, PromoAdmin)