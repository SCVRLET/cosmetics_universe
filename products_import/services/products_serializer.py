import aiohttp

from asgiref.sync import sync_to_async

import re

import requests

import io

from ..models import Offer, Product, ProductBrand, ProductCategory, Shop


class ProductsSerializer:
	def _get_full_image_link(self, site_url: str, image_link: str) -> str:
		if re.match(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)', image_link):
			return image_link

		return site_url + image_link

	def _get_image_format(self, image_link: str) -> str:
		image_name_and_format = image_link.split('/')[-1]

		if '.' in image_name_and_format:
			return image_name_and_format.split('.')[-1]

		return 'jpeg'

	async def save_or_update(self, site_name: str, products_info: dict) -> None:
		category = products_info['category']
		image_link = products_info['product_image_link']
		description = products_info['description']

		offers = products_info['offers']

		brand_obj, _ = await sync_to_async(ProductBrand.objects.update_or_create)(
			title=products_info['brand']
			)

		category_obj = await sync_to_async(ProductCategory.objects.get)(title=category)

		shop_obj = await sync_to_async(Shop.objects.get)(title=site_name)

		product_obj, created = await sync_to_async(Product.objects.update_or_create)(
			title=products_info['product_name'],
			source_link=products_info['source_link'],
			brand=brand_obj,
			category=category_obj,
			shop=shop_obj,
			description=description[:1000] if description else '',
			)

		if created:
			image_format = self._get_image_format(image_link)
			saved_image_name = f'{product_obj.id}.{image_format}'

			site_url = shop_obj.url

			full_image_link = self._get_full_image_link(site_url, products_info['product_image_link'])

			try:
				async with aiohttp.ClientSession(headers=requests.utils.default_headers()) as session:
					async with session.get(url=full_image_link) as image:
						image_content = await image.read()
						
						with io.BytesIO(image_content) as image_file:
							await sync_to_async(product_obj.image.save)(saved_image_name, image_file)

			except:
				print('Error with image download')

		for offer in offers:
			await sync_to_async(Offer.objects.update_or_create)(
				product=product_obj,
				price_without_discount=offer['price_without_discount'],
				discount = offer['discount'],
				is_available=offer['is_available']
				)