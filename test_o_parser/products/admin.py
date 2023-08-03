from django.contrib import admin

from .models import Product


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'new_price', 'old_price', 'image_url', 'url', 'product_code')
    search_fields = ['name'] 

admin.site.register(Product)
