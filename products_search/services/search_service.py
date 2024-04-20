from django.db.models import Q

from products_import.models import Product


def search_products(search_query=None):
	if search_query:
		return Product.objects.filter(
			Q(title__icontains=search_query) | Q(description__icontains=search_query)
		).order_by('title')
	else:
		return Product.objects.all().order_by('title')