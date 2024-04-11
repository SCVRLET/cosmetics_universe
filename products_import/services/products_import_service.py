import aiofiles

import asyncio

import aiohttp

from .parsers import parser_getter

import urllib.parse

import datetime

import requests

from os.path import join as path_join

from django.conf import settings

from .parsers.base_parser import BaseParser

from .products_serializer import ProductsSerializer


class ProductsImporter:

	IMPORT_IS_RUNNING = 0

	def __init__(self, products_import_file_path='', products_error_log_file_path=''):
		curr_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
		products_import_dir_path = settings.PRODUCTS_IMPORT_DIR_PATH

		self.products_import_file_path = path_join(products_import_dir_path, f'products_import{curr_date}.txt') \
		if not products_import_file_path else products_import_file_path

		self.products_error_log_file_path = path_join(products_import_dir_path, f'products_import{curr_date}_errors.log') \
		if not products_error_log_file_path else products_error_log_file_path

		self._async_tasks = []
		self._chunk_size = 90

	def _get_protocol_and_host_from_url(self, url: str) -> str:
		parts = urllib.parse.urlparse(url)

		return f'{parts.scheme}://{parts.netloc}'

	async def _add_to_log(self, log_text: str) -> None:
		async with aiofiles.open(self.products_error_log_file_path, mode='a') as file:
			await file.write(datetime.date.today().isoformat() + log_text + '\n\n')


	async def _save_products_info_in_file(self, products_info: dict) -> None:
		async with aiofiles.open(self.products_import_file_path, mode='a') as file:
			await file.write(str(products_info) + '\n')

	async def _save_products_info_in_db(self, site_name: str, product_category: str, product_page_url: str, products_info: dict) -> None:
		products_info['category'] = product_category
		products_info['source_link'] = product_page_url

		await ProductsSerializer().save_or_update(site_name, products_info)

	async def _run_async_tasks(self):
		chunks = (self._async_tasks[pos:pos + self._chunk_size] for pos in range(0, len(self._async_tasks), self._chunk_size))

		for chunk in chunks:
			await asyncio.gather(*chunk)


	async def _import_products_from_catalog(self, site_name: str, products_category: str, catalog_url: str, test_mode=False) -> None:
		parser = parser_getter.ParserGetter().get_parser(site_name)

		catalog_page_html = requests.get(url=catalog_url).text

		base_url = self._get_protocol_and_host_from_url(catalog_url)

		catalog_pages_number = parser.get_number_of_pages_in_catalog(catalog_page_html)

		async with aiohttp.ClientSession(headers=requests.utils.default_headers()) as session:
			for page_num in range(1, catalog_pages_number+1):
				query = {parser.get_pagination_key(): page_num}

				catalog_page_html = requests.get(catalog_url, params=query).text

				product_cards = parser.get_product_cards_from_catalog_page(catalog_page_html)

				for product_card in product_cards:
					if parser.is_product_available_from_product_card(product_card):
						product_page_url = base_url + parser.get_product_link_from_product_card(product_card)

						self._async_tasks.append(self._import_product_info_from_products_page(parser, site_name, products_category, product_page_url, session))

			await self._run_async_tasks()

	async def _import_product_info_from_products_page(self, parser: BaseParser, site_name: str,
	 												product_category: str, product_page_url: str, session: aiohttp.ClientSession) -> None:
		parser = parser_getter.ParserGetter().get_parser(site_name)

		async with session.get(url=product_page_url) as response:
			if response.status == 200:
				product_page_html = await response.text()

				product_info = parser.get_info_from_product_page(product_page_html)

				await self._save_products_info_in_db(site_name, product_category, product_page_url, product_info)

	async def run_import(self, site_name: str, products_category: str, catalog_url: str, test_mode=False):
		self.__class__.IMPORT_IS_RUNNING = 1

		await self._import_products_from_catalog(site_name, products_category, catalog_url)

		self.__class__.IMPORT_IS_RUNNING = 0