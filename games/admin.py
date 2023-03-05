from django.contrib import admin
from .models import *

# Register your models here.
class RatingSetAdminInline(admin.StackedInline):
    model = RatingSet
    readonly_fields = ('game',)
    filter_horizontal = ['esrb_ratings',]
    can_delete = False


class GameAdmin(admin.ModelAdmin):
    inlines = (RatingSetAdminInline,)
    readonly_fields = ('id', 'slug','final_price_with_prefix', 'promo_percentage_with_suffix',
                       'promo', 'in_promo',)
    list_display = ('id', 'name','slug',
                    'publisher', 'release_date', 'base_price',
                    'in_promo', 'promo_percentage_with_suffix',
                    'final_price_with_prefix',)
    filter_horizontal = ['developers', 'platforms', 'tags',
                         'genres','media',]
    fields = ('id', 'name', 'slug', 'platforms', 'developers', 'publisher',
              'genres', 'tags', 'media', 'base_price',
              'in_promo', 'promo', 'promo_percentage_with_suffix',
              'final_price_with_prefix',)


class DLCAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'slug','final_price_with_prefix', 'promo_percentage_with_suffix',
                    'promo', 'in_promo',)
    list_display = ('id', 'name','slug',
                    'publisher', 'release_date', 'base_price',
                    'in_promo', 'promo_percentage_with_suffix',
                    'final_price_with_prefix')
    filter_horizontal = ['developers', 'tags','media',]
    fields = ('id', 'name', 'slug', 'developers', 'publisher',
            'tags', 'media', 'in_promo', 'promo',
            'promo_percentage_with_suffix', 'final_price_with_prefix',)


class RatingSetAdmin(admin.ModelAdmin):
    readonly_fields = ('game',)
    filter_horizontal = ['esrb_ratings',]


admin.site.register(Game, GameAdmin)
admin.site.register(DLC, DLCAdmin)
admin.site.register(Genre)
admin.site.register(Publisher)
admin.site.register(Developer)
admin.site.register(RatingSet, RatingSetAdmin)
admin.site.register(EsrbRating)
admin.site.register(Platform)
admin.site.register(Tag)
admin.site.register(Media)