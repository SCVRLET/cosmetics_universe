import requests

from .parsers import parser_getter

import urllib.parse

import datetime

from os.path import join as path_join

from django.conf import settings

from .parsers.base_parser import BaseParser


CURR_DATE = datetime.date.today().isoformat()
PRODUCTS_IMPORT_DIR_PATH = settings.PRODUCTS_IMPORT_DIR_PATH

PRODUCTS_IMPORT_FILE_PATH = path_join(PRODUCTS_IMPORT_DIR_PATH, f'products_import{CURR_DATE}.txt')
PRODUCTS_ERRORS_LOG_FILE_PATH = path_join(PRODUCTS_IMPORT_DIR_PATH, f'products_import{CURR_DATE}_errors.log')

def _get_protocol_and_host_from_url(url: str) -> str:
	parts = urllib.parse.urlparse(url)

	return f'{parts.scheme}://{parts.netloc}'


def _add_to_log(log_text: str) -> None:
	with open(PRODUCTS_ERRORS_LOG_FILE_PATH, 'a') as f:
		f.write(datetime.date.today().isoformat(), log_text, '\n\n')


def _save_products_info_in_file(products_info: str) -> None:
	with open(PRODUCTS_IMPORT_FILE_PATH, 'a') as f:
		f.write(str(products_info) + '\n')


# TODO: СДЕЛАТЬ ДЕКОРАТОР ДЛЯ ОБРАБОТКИ ОШИБОК С ЗАПРОСАМИ


def _import_products_from_catalog(site_name: str, products_category: str, catalog_url: str, test_mode=False) -> None:
	parser = parser_getter.ParserGetter().get_parser(site_name)

	catalog_page_response = requests.get(catalog_url)

	catalog_page_html = catalog_page_response.text
	base_url = _get_protocol_and_host_from_url(catalog_url)

	catalog_pages_number = parser.get_number_of_pages_in_catalog(catalog_page_html)

	for page_num in range(1, catalog_pages_number+1):
		query = {parser.get_pagination_key(): page_num}

		catalog_page_html = requests.get(catalog_url, params=query).text

		product_cards = parser.get_product_cards_from_catalog_page(catalog_page_html)

		for product_card in product_cards:
			if parser.is_product_available_from_product_card(product_card):
				product_page_url = base_url + parser.get_product_link_from_product_card(product_card)

				_import_product_info_from_products_page(parser, site_name, products_category, product_page_url)


def _import_product_info_from_products_page(parser: BaseParser, site_name: str, product_category: str, product_page_url: str) -> None:
	parser = parser_getter.ParserGetter().get_parser(site_name)

	product_page_response = requests.get(product_page_url)

	try:
	    product_page_response.raise_for_status()

	except requests.exceptions.HTTPError as e:
	    _add_to_log(repr(e))

	    return

	else:
		product_page_html = product_page_response.text

		product_info = parser.get_info_from_product_page(product_page_html)

		_save_products_info_in_file(product_info)

		# ЕСЛи ТОВАР ЕСТЬ, ТО ОБНОВЛЯЕМ ИНФУ

		# ЕСЛИ ТОВАРА НЕТ, ДОБАВЛЯЕМ В БАЗУ:
		# 1)Товар
		# 2)Бренд
		# 3)Предложение

def run_import(site_name: str, products_category: str, catalog_url: str, test_mode=False):
	_import_products_from_catalog(site_name, products_category, catalog_url)