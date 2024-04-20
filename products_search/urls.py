from .views import products_catalog

from django.urls import path, include


app_name = 'products_search'

urlpatterns = [
    path('products_catalog/', products_catalog, name='products_catalog'),
 ]