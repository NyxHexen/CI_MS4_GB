from django.contrib import admin
from .models import *

# Register your models here.
class RatingSetAdminInline(admin.StackedInline):
    model = RatingSet
    readonly_fields = ('game',)
    can_delete = False


class GameAdmin(admin.ModelAdmin):
    inlines = (RatingSetAdminInline,)
    readonly_fields = ('id', 'slug','final_price_with_prefix', 'promo_percentage_with_suffix',
                       'promo', 'in_promo',)
    list_display = ('id', 'name','slug',
                    'release_date', 'base_price', 'is_featured', 'carousel',
                    'in_promo', 'promo_percentage_with_suffix',
                    'final_price_with_prefix',)
    filter_horizontal = ['developers', 'publishers', 'platforms', 'tags',
                         'genres','media', 'features',]
    fields = ('id', 'name', 'slug', 'release_date', 'platforms', 'developers', 'publishers',
              'genres', 'tags', 'features', 'media', 'is_featured', 'carousel', 'base_price',
              'in_promo', 'promo', 'promo_percentage_with_suffix',
              'final_price_with_prefix',)


class DLCAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'slug','final_price_with_prefix', 'promo_percentage_with_suffix',
                    'promo', 'in_promo',)
    list_display = ('id', 'name','slug',
                    'release_date', 'base_price', 'is_featured', 'carousel',
                    'in_promo', 'promo_percentage_with_suffix',
                    'final_price_with_prefix')
    filter_horizontal = ['developers', 'publishers', 'tags','media',]
    fields = ('id', 'name', 'release_date', 'slug', 'developers', 'publishers',
            'tags', 'media', 'is_featured', 'carousel', 'in_promo', 'promo',
            'promo_percentage_with_suffix', 'final_price_with_prefix',)


class RatingSetAdmin(admin.ModelAdmin):
    readonly_fields = ('game',)


admin.site.register(Game, GameAdmin)
admin.site.register(DLC, DLCAdmin)
admin.site.register(Genre)
admin.site.register(Publisher)
admin.site.register(Developer)
admin.site.register(RatingSet, RatingSetAdmin)
admin.site.register(EsrbRating)
admin.site.register(PegiRating)
admin.site.register(UserRating)
admin.site.register(Platform)
admin.site.register(Feature)
admin.site.register(Tag)
admin.site.register(Media)