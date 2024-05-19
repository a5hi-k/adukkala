from django.contrib import admin
from . models import Product,Variation,ReviewRating,Advertisement  #ProductGallery
import admin_thumbnails

# Register your models here.

# @admin_thumbnails.thumbnail('image')
# class ProductGalleryInline(admin.TabularInline):
#     model = ProductGallery
#     extra = 1



class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug':( 'product_name', )}
    # inlines = [ProductGalleryInline]


# since we are returning the variations as object using unicode we need this to see the variations names in the admin panel
class VariationAdmin(admin.ModelAdmin):
    list_display = ('product','variation_category','variation_value','is_active')
    list_editable = ('is_active',)
    list_filter = ('product','variation_category','variation_value')


admin.site.register(Product,ProductAdmin)
admin.site.register(Variation,VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(Advertisement)
# admin.site.register(ProductGallery)