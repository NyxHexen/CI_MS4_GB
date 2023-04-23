# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.contrib import admin

# Local
from .models import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class RatingSetAdminInline(admin.StackedInline):
    model = RatingSet
    readonly_fields = (
        "game",
        "dlc"
        )
    can_delete = False
    fields = (
        "esrb_rating",
        "pegi_rating"
        )


class GameAdmin(admin.ModelAdmin):
    inlines = (RatingSetAdminInline,)
    readonly_fields = (
        "id",
        "slug",
        "final_price_with_prefix",
        "promo_percentage_with_suffix",
        "promo",
        "in_promo",
    )
    list_display = (
        "id",
        "name",
        "slug",
        "release_date",
        "base_price",
        "is_featured",
        "carousel",
        "in_promo",
        "promo_percentage_with_suffix",
        "final_price_with_prefix",
    )
    filter_horizontal = [
        "developers",
        "publishers",
        "platforms",
        "tags",
        "genres",
        "media",
        "features",
    ]
    fields = (
        "id",
        "name",
        "slug",
        "release_date",
        "storyline",
        "description",
        "platforms",
        "developers",
        "publishers",
        "genres",
        "tags",
        "features",
        "media",
        "is_featured",
        "carousel",
        "base_price",
        "in_promo",
        "promo",
        "promo_percentage_with_suffix",
        "final_price_with_prefix",
    )


class DLCAdmin(admin.ModelAdmin):
    inlines = (RatingSetAdminInline,)
    readonly_fields = (
        "id",
        "slug",
        "final_price_with_prefix",
        "promo_percentage_with_suffix",
        "promo",
        "in_promo",
    )
    list_display = (
        "id",
        "name",
        "slug",
        "release_date",
        "base_price",
        "is_featured",
        "carousel",
        "in_promo",
        "promo_percentage_with_suffix",
        "final_price_with_prefix",
    )
    filter_horizontal = [
        "developers",
        "publishers",
        "platforms",
        "tags",
        "genres",
        "media",
        "features",
    ]
    fields = (
        "id",
        "required_game",
        "name",
        "slug",
        "release_date",
        "storyline",
        "description",
        "platforms",
        "developers",
        "publishers",
        "genres",
        "tags",
        "features",
        "media",
        "is_featured",
        "carousel",
        "base_price",
        "in_promo",
        "promo",
        "promo_percentage_with_suffix",
        "final_price_with_prefix",
    )


class RatingSetAdmin(admin.ModelAdmin):
    readonly_fields = (
        "game",
        "dlc"
        )
    list_display = (
        'esrb_rating',
        'pegi_rating',
        'game',
        'dlc'
    )
    list_display_links = (
        'esrb_rating',
        'pegi_rating',
        'game',
        'dlc'
    )
    
class DeveloperAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'official_site',
        'country',
    )

class PlatformAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'official_site',
        'country',
    )

class PublisherAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'official_site',
        'country',
    )


admin.site.register(Game, GameAdmin)
admin.site.register(DLC, DLCAdmin)
admin.site.register(Genre)
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Developer, DeveloperAdmin)
admin.site.register(RatingSet, RatingSetAdmin)
admin.site.register(EsrbRating)
admin.site.register(PegiRating)
admin.site.register(UserRating)
admin.site.register(Platform, PlatformAdmin)
admin.site.register(Feature)
admin.site.register(Tag)
