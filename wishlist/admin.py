
from django.contrib import admin
from . models import Wishlist,WishlistItem

# Register your models here.

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('wishlist_id','date_added')


# since we are returning the variations as object using unicode we need this to see the variations names in the admin panel
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('product','wishlist','is_active')



admin.site.register(Wishlist,WishlistAdmin)
admin.site.register(WishlistItem,WishlistItemAdmin)