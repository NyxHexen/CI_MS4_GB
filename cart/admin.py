# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django:
from django.contrib import admin

# Internal:
from .models import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class CartItemsInline(admin.TabularInline):
    """
    Admin class forr the CartItem inline in CartAdmin.
    """
    model = CartItem
    readonly_fields = (
        'cart',
        'price'
        )
    can_delete = False


class CartAdmin(admin.ModelAdmin):
    """
    Admin class for the Cart model.
    """
    inlines = (CartItemsInline,)
    list_display = (
        'user',
        'created_date',
        'updated_date',
        'total_in_cart',
        )
    readonly_fields = (
        'user',
        'created_date',
        'updated_date'
    )


admin.site.register(Cart, CartAdmin)
