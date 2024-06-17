from products_import.models import Product

def filter_products(products, category_ids:list=None, brand_ids:list=None, shop_ids:list=None):
	if category_ids:
		products = products.filter(category__in=category_ids)
	if brand_ids:
		products = products.filter(brand__in=brand_ids)
	if shop_ids:
		products = products.filter(shop__in=shop_ids)

	return products