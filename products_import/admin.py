from django.contrib import admin

from .models import Offer, Product, ProductBrand, ProductCategory, Shop

# Register your models here.
admin.site.register(Offer)
admin.site.register(Product)
admin.site.register(ProductBrand)
admin.site.register(ProductCategory)
admin.site.register(Shop)