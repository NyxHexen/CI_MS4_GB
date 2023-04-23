from django.contrib import admin
from .models import *

# Register your models here.
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