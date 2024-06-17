from asgiref.sync import sync_to_async, async_to_sync	

from django.contrib.admin.views.decorators import staff_member_required

from django.http import JsonResponse

from django.shortcuts import render

from .services import compare_products_ai_service

@sync_to_async
@staff_member_required
@async_to_sync
async def merge_products(request):
    await compare_products_ai_service.run_import()

    return JsonResponse({'ok': True})
