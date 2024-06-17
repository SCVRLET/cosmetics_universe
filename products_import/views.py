from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async, async_to_sync
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

import time

from .forms import ProductsImportForm
from .services.products_import_service import ProductsImporter


class ProductsImportView(View):
	@sync_to_async
	@method_decorator(staff_member_required)
	@async_to_sync
	async def get(self, request):
		form = ProductsImportForm()

		return render(request, 'admin/products_import.html', {'products_import_form': form})

	@sync_to_async
	@csrf_exempt
	@method_decorator(staff_member_required)
	@async_to_sync
	async def post(self, request):
		form = ProductsImportForm(request.POST)

		if form.is_valid():
			data = form.cleaned_data
			await ProductsImporter().run_import(data['shop_choice'], data['category_choice'], data['url'] )

			return JsonResponse({'ok': True})


@csrf_exempt
def ajax_products_import_status(request):
	if request.method == 'GET':
		import_status = ProductsImporter().IMPORT_IS_RUNNING

		message = "Импортирование запущено" if import_status else "Импортирование завершено"

		return JsonResponse({'status': message})