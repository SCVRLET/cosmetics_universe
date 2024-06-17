import asyncio

from PIL import Image

import openai

from django.conf import settings

from products_import.models import Product, Offer

from base64 import b64encode

from asgiref.sync import sync_to_async

from openai import AsyncOpenAI


client = AsyncOpenAI(api_key=settings.AI_API_KEY)

async def compare_products(product1, product2):
	messages = [
		{
			"role": "user",
			"content": f"""
				Compare these products and return 1 if same, 0 if different (only one symbol needed):
				Product 1: {product1.title}, {product1.description[:150]}
				![Product 1 Image]({product1.image_source_link})
				Product 2: {product2.title}, {product2.description[:150]}
				![Product 2 Image]({product2.image_source_link})
			"""
		}
	]

	response = await client.chat.completions.create(
		model="gpt-4o",
		messages=messages,
		max_tokens=1
	)

	return int(response.choices[0].message.content.strip()) if response.choices[0].message.content.strip().isnumeric() else 0


async def merge_products(product1, product2):
	offers_to_update = await sync_to_async(list)(Offer.objects.filter(product=product1))

	for offer in offers_to_update:
		offer.product = product2
		await sync_to_async(offer.save)()

	product2.source_link += f', {product1.source_link}'
	await sync_to_async(product2.save)()
	await sync_to_async(product1.delete)()


async def process_group(products):
	for i, product1 in enumerate(products):
		for product2 in products[i+1:]:

			is_same = await compare_products(product1, product2)

			if is_same:
				await merge_products(product1, product2)


async def group_products_by_brand_and_category():
	products =  await sync_to_async(lambda: list(Product.objects.all().select_related('brand', 'category')))()
	grouped_products = {}

	for product in products:
		key = (product.brand, product.category)
		if key not in grouped_products:
			grouped_products[key] = []
		grouped_products[key].append(product)

	return grouped_products


async def run_import():
	grouped_products = await group_products_by_brand_and_category()

	tasks = []

	for group in grouped_products.values():
		tasks.append(process_group(group)

	await asyncio.gather(*tasks)