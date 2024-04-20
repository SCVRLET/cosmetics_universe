from django.shortcuts import render

from django.core.paginator import Paginator

from .forms import ProductsFilterForm

from .services.filter_service import filter_products

from .services.search_service import search_products

def products_catalog(request):
	if request.method == 'GET':

		filter_form = ProductsFilterForm(request.GET)

		category_ids = filter_form['category_choice'].value()
		brand_ids = filter_form['brand_choice'].value()
		shop_ids = filter_form['shop_choice'].value()

		search_query = request.GET.get('search_q', '')

		searched_products = search_products(search_query)

		filtered_products = filter_products(searched_products, category_ids, brand_ids, shop_ids)

		paginator = Paginator(filtered_products, 50)
		page_number = request.GET.get('page', 1)
		products = paginator.page(page_number)
		
		get_copy = request.GET.copy()

		parameters = get_copy.pop('page', True) and get_copy.urlencode()


		return render(request, 'main/products_catalog.html', {'filter_form': filter_form, 'search_string': search_query, 'products': products, "parameters": parameters})