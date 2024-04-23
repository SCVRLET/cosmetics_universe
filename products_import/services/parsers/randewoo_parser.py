import re

import requests

from bs4 import BeautifulSoup

from .base_parser import BaseParser


class RandewooParser(BaseParser):
	def _get_product_name(self, product_page_html: BeautifulSoup) -> str:
		return product_page_html.find('h1', class_='b-header__titleAndLogoInner').find('div', class_='b-header__subtitle').string

	def _get_product_size(self, product_page_html: BeautifulSoup) -> str:
		return product_page_html.find('h1', class_='b-header__titleAndLogoInner').find('div', class_='b-header__subtitle').string.split()[-1]

	def _get_offer_size(self, offer_block_html: BeautifulSoup) -> str:
		size_block_text = offer_block_html.find('a', class_='s-productType__titleText').text

		return size_block_text.split()[-1] if size_block_text else ''

	def _get_product_description(self, product_page_html: BeautifulSoup) -> str:
		description_tag = product_page_html.find('div', class_='collapsable')
		
		return description_tag.find_all('p')[0].text if description_tag else None

	def _get_product_brand(self, product_page_html: BeautifulSoup) -> str:
		return product_page_html.find('div', class_='b-header__mainTitle').string

	def _get_product_img_link(self, product_page_html: BeautifulSoup) -> str:
		return product_page_html.find('div', class_='slider__img').find('img', class_='js-main-product-image')['src']

	def _is_offer_available(self, offer: BeautifulSoup) -> bool:
		return not bool(offer.find('div', class_='s-productType__priceNotAvailable'))

	def _is_product_available(self, price_block: BeautifulSoup) -> bool:
		return not price_block.string == 'Нет в наличии'

	def is_product_available_from_product_card(self, product_card_html: BeautifulSoup) -> bool:
		return 'b-catalogItem--unavailable' not in product_card_html['class']

	def get_number_of_pages_in_catalog(self, catalog_page_html: str) -> int:
		soup = BeautifulSoup(catalog_page_html, 'html.parser')

		pager_items = soup.find_all('li', class_='pager__item')

		if pager_items:
			page_last_number = int(pager_items[-2].find('span').text)

			return page_last_number

		return 1

	def get_product_cards_from_catalog_page(self, catalog_page_html: str) -> list:
		soup = BeautifulSoup(catalog_page_html, 'html.parser')

		return soup.find_all('li', class_='products__item js-products__item b-catalogItem')

	def get_product_link_from_product_card(self, product_card_html: BeautifulSoup) -> str:
		return product_card_html.find('a', class_='b-catalogItem__descriptionLink')['href']

	def get_info_from_product_page(self, product_page_html: str):
		soup = BeautifulSoup(product_page_html, 'html.parser')

		product_name = self._get_product_name(soup)
		product_image_link = self._get_product_img_link(soup)

		offers = []

		product_types = soup.find_all('li', class_='s-productType')

		if product_types:
			for offer in product_types:
				offer_info = {}

				size = self._get_offer_size(offer)
				is_available = self._is_offer_available(offer)

				offer_info.update({'size': size, 'is_available': is_available, 'price_without_discount': 0, 'discount': 0})

				if is_available:
					price_block = offer.find('div', class_='s-productType__price')

					discount_tag = price_block.find('span', class_='s-productType__priceDiscount')

					if discount_tag:
						price_without_discount = price_block.find('span', class_='s-productType__priceOldValue').text
						discount = re.findall(r'\d+', discount_tag.text)[0]

					else:
						discount = 0
						price_without_discount = price_block.find('span', class_='s-productType__priceNewValue').text

					offer_info.update({'discount': discount, 'price_without_discount': price_without_discount})

				offers.append(offer_info) 

		else:
			size = self._get_product_size(soup)
			price_block = soup.find('div', class_='b-productSummary__priceWrapper')

			is_available = self._is_product_available(price_block)

			offer_info = {'size': size, 'is_available': is_available, 'price_without_discount': 0, 'discount': 0}

			if is_available:
				discount_tag = price_block.find('span', class_='s-productType__priceDiscount__monoItem')

				if discount_tag:
					price_without_discount = price_block.find('s', class_='b-productSummary__priceOriginal').string
					discount = re.findall(r'\d+', discount_tag.text)[0]

				else:
					discount = 0
					price_without_discount = int(price_block.find('strong', 'b-productSummary__priceNew').string)

				offer_info.update({'discount': discount, 'price_without_discount': price_without_discount})

			offers.append(offer_info) 

		brand = self._get_product_brand(soup)

		description = self._get_product_description(soup)

		return {
			'product_name': product_name,
			'brand': brand,
			'description': description,
			'offers': offers,
			'product_image_link': product_image_link,
		}

	def get_pagination_url_part(self) -> str:
		return '?&page='