from .views import ProductsImportView, ajax_products_import_status

from django.urls import path, include

from django.contrib.auth.decorators import user_passes_test


app_name = 'products_import'

urlpatterns = [
    path('admin-import-products/', ProductsImportView.as_view(), name='products_import'),
    path('ajax-products-import-status/', ajax_products_import_status, name='ajax_products_import_status'),
 ]