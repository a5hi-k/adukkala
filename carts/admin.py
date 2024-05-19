from django.contrib import admin
from . models import Cart,CartItem

# Register your models here.

class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id','date_added')


# since we are returning the variations as object using unicode we need this to see the variations names in the admin panel
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product','cart','quantity','is_active')



admin.site.register(Cart,CartAdmin)
admin.site.register(CartItem,CartItemAdmin)