from bs4 import BeautifulSoup

from .base_parser import BaseParser


class PodrygkaParser(BaseParser):
	def _get_product_weight(self, product_name: str) -> str:
		return ' '.join(product_name.split()[-2:])

	def _get_product_description(self, product_page_html: BeautifulSoup) -> str:
		return product_page_html.find('div', class_='block-text-hidden').find('div', class_='__text').text

	def _get_product_brand(self, product_page_html: BeautifulSoup) -> str:
		return product_page_html.find('div', class_='product-detail__brand').find('img')['alt']

	def _get_product_name(self, product_page_html: BeautifulSoup) -> str:
		return product_page_html.find('h1', class_='name_section').string

	def _get_product_img_link(self, product_page_html: BeautifulSoup) -> str:
		return product_page_html.find('div', class_='product-detail__gallery-slider-item').find('img')['src']

	def _is_product_available(self, product_page_html: BeautifulSoup) -> bool:
		return not bool(product_page_html.find('span', class_='not-available'))

	def is_product_available_from_product_card(self, product_card_html: BeautifulSoup) -> bool:
		return not product_card_html.find('span', class_='not-available')

	def get_product_cards_from_catalog_page(self, catalog_page_html: str) -> list:
		soup = BeautifulSoup(catalog_page_html, 'html.parser')

		return soup.find_all('div', class_='item-product-card')

	def get_number_of_pages_in_catalog(self, catalog_page_html: str) -> int:
		soup = BeautifulSoup(catalog_page_html, 'html.parser')

		pag_last_button = soup.find('a', class_='pagination__text pagination-backward')

		last_page_link = pag_last_button['href']

		page_last_number = int(last_page_link.split('/')[-1].split('=')[-1])

		return page_last_number

	def get_info_from_product_page(self, product_page_html: str):
		soup = BeautifulSoup(product_page_html, 'html.parser')

		product_image_link = self._get_product_img_link(soup)
		product_name = self._get_product_name(soup)
		weight = self._get_product_weight(product_name)
		is_available = self._is_product_available(soup)

		price_without_discount_block = soup.find('span', class_='price__item--old')

		discount = 0

		if price_without_discount_block:
			price_without_discount = int(price_without_discount_block.find('span', class_='price_value').string)
			price_with_discount = int(soup.find('span', 'price__item--current').find('span', class_='price_value').string)
			discount = round( (price_without_discount - price_with_discount) * 100 / price_without_discount )

		else:
			price_without_discount = int(soup.find('span', 'price__item--current').find('span', class_='price_value').string)

		brand = self._get_product_brand(soup)
		description = self._get_product_description(soup)

		return {
			'product_name': product_name,
			'brand': brand,
			'description': description,
			'offers': [{
				'size': f'{weight}',
				'price_without_discount': price_without_discount,
				'discount': discount, 'is_available': is_available
			}],
			'product_image_link': product_image_link
		}

	def get_pagination_key(self):
		return 'PAGEN_1'

	def get_product_link_from_product_card(self, product_card_html: BeautifulSoup) -> str:
		return product_card_html.find('a', class_='products-list-item__title')['href']