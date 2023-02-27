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

    list_display = ('id', 'name','slug',
                    'publishers', 'release_date', 'base_price',
                    'in_promo', 'final_price')
    filter_horizontal = ['developers', 'platforms', 'tags',
                         'genres','media',]
    list_editable = ('in_promo',)
    

class RatingSetAdmin(admin.ModelAdmin):
    readonly_fields = ('game',)
    filter_horizontal = ['esrb_ratings',]


admin.site.register(Game, GameAdmin)
admin.site.register(DLC)
admin.site.register(Genre)
admin.site.register(Publisher)
admin.site.register(Developer)
admin.site.register(RatingSet, RatingSetAdmin)
admin.site.register(EsrbRating)
admin.site.register(Platform)
admin.site.register(Tag)
admin.site.register(Media)