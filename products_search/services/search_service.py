from django.db.models import Q
from django.contrib.postgres.search import SearchVector

from products_import.models import Product


def search_products(search_query:list=None):
	if search_query:
		return Product.objects.annotate(
			search = SearchVector('title', 'description')
		).filter(search=search_query)
	else:
		return Product.objects.all().order_by('title')