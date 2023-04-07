from django.contrib import admin
from .models import *

# Register your models here.
class CartItemsInline(admin.TabularInline):
    model = CartItem
    readonly_fields = ('cart', 'price')
    can_delete = False

class CartAdmin(admin.ModelAdmin):
    inlines = (CartItemsInline,)

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)