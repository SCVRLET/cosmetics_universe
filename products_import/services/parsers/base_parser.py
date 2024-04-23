import requests

from bs4 import BeautifulSoup


class BaseParser:
	'''
		Информация, которая выбирается у каждого товара в интернет-магазине:

		1)Название товара (product_name)
		2)Название бренда товара (brand)
		3)Описание товара (description)
		4)Для конкретной характеристики товара
		(кобминация размера (size) + цена без скидки (price_without_discount) + скидка (discount) + наличие)
		6)Страница товара в магазине
		7)Ссылку на изображение с товаром
	'''

	def get_info_from_product_page(self, product_page_html: str) -> dict:
		'''
			Извлекает и возвращает информацию о товаре в структуре следующего вида:
			{
				'product_name': 'Гигиеническая губная помада Аевит 4г (жирная)',
				'sex': None,
				'brand': 'Librederm',
				'description': 'От производителя:',
				'offers': [{'size': '(жирная)', 'price_without_discount': '269', 'discount': '20'}],
				'product_link': 'https://randewoo.ru/product/gigienicheskaya-gubnaya-pomada-zhirnaya-aevit-4g?source_category=7',
				'product_image_link': 'https://cdn2.randewoo.ru/img/186473/n/1'
			}

		'''
		return

	def get_number_of_pages_in_catalog(self, catalog_page_html: str) -> int:
		return

	def get_product_cards_from_catalog_page(self, catalog_page_html: str) -> list:
		return

	def get_pagination_url_part(self) -> str:
		return

	def get_product_url_from_product_card(self, product_card: BeautifulSoup) -> str:
		return

	def is_product_available_from_product_card(self, product_card_html: BeautifulSoup) -> bool:
		return