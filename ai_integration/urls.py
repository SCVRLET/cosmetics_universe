from .views import merge_products

from django.urls import path, include


app_name = 'ai_integration'

urlpatterns = [
    path('merge_products/', merge_products, name='merge_products'),
 ]