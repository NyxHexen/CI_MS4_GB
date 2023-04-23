from django.contrib import admin
from .models import Order, OrderLineItem

# Register your models here.


class OrderLineItemAdminInline(admin.TabularInline):
    """
    TabularInline class for the OrderLineItem inline in OrderAdmin.
    """
    model = OrderLineItem
    readonly_fields = (
        "price",
        )


class OrderAdmin(admin.ModelAdmin):
    """
    Admin class for the Order model.
    """
    inlines = (OrderLineItemAdminInline,)
    readonly_fields = (
        "order_number",
        "date",
        "order_total",
        "original_cart",
        "stripe_pid",
    )

    fields = (
        "order_number",
        "full_name",
        "email",
        "phone_number",
        "country",
        "postcode",
        "town_or_city",
        "street_address1",
        "street_address2",
        "county",
        "date",
        "order_total",
        "original_cart",
        "stripe_pid",
    )

    list_display = (
        "order_number",
        "date",
        "full_name",
        "order_total",
    )

    ordering = ("-date",)

class OrderLineItemAdmin(admin.ModelAdmin):
    list_display = (
        'game',
        'dlc',
        'quantity',
        'price'
    )


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLineItem, OrderLineItemAdmin)
