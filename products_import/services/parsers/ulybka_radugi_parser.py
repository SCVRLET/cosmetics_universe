from bs4 import BeautifulSoup

from .base_parser import BaseParser


class UlybkaRadugiParser(BaseParser):
	def _get_product_weight(self, product_name: str) -> str:
		return ' '.join(product_name.split()[-2:])

	def _get_product_description(self, product_page_html: BeautifulSoup) -> str:
		description_block = product_page_html.find('div', class_='det-info-descr text-in-content')

		if description_block:

			return description_block.find_all('p')[1].string

		return ''

	def _get_product_brand(self, product_page_html: BeautifulSoup) -> str:
		details_block = product_page_html.find('div', class_='props-col-wrp clear-n')
		brands_block = details_block.find_all('div', class_='props-col')[0].find_all('ul', class_='props-el')[1]
		manufacturer_about = brands_block.find('li', class_='active').find_all('li')

		brand = 'Неизвестно'
		for manufacturer_info in manufacturer_about:
			if manufacturer_info.find('span', class_='name').string == 'Бренды:':
				brand =  manufacturer_info.find('span', class_='val').find('a').string

		return brand if brand else 'Неизвестно'

	def _get_product_name(self, product_page_html: BeautifulSoup) -> str:
		return product_page_html.find('div', class_='title-page').find('h1').string

	def _get_product_img_link(self, product_page_html: BeautifulSoup) -> str:
		return product_page_html.find('div', class_='slick-product-detail-view').find('picture').find('img')['data-src']

	def _is_product_available(self, product_page_html: BeautifulSoup) -> bool:
		return True

	def is_product_available_from_product_card(self, product_card_html: BeautifulSoup) -> bool:
		return not bool(product_card_html.find('span', class_='not-available tooltip tooltipstered'))

	def get_product_cards_from_catalog_page(self, catalog_page_html: str) -> list:
		soup = BeautifulSoup(catalog_page_html, 'html.parser')

		return soup.find_all('a', {'class': ['prod-item', 'experiment', 'in-store']})

	def get_number_of_pages_in_catalog(self, catalog_page_html: str) -> int:
		soup = BeautifulSoup(catalog_page_html, 'html.parser')

		pagination_top_block = soup.find('div', class_='sort-by pager-nav top')

		if pagination_top_block:
			return int(pagination_top_block.find('div', class_='pager').find_all('a')[-2].string)

		return 1

	def get_info_from_product_page(self, product_page_html: str):
		soup = BeautifulSoup(product_page_html, 'html.parser')

		product_image_link = self._get_product_img_link(soup)
		product_name = self._get_product_name(soup)
		weight = self._get_product_weight(product_name)
		is_available = self._is_product_available(soup)

		discount_block = soup.find('span', class_='prod-item-labels__label prod-item-labels__label--disco')
		price_block = soup.find('div', class_='price')

		if discount_block:
			discount = int(discount_block.string.split()[1].replace('%', ''))
			price_without_discount = int(price_block.find('span', 'price-offline__old-price').string.split()[0])

		else:
			discount = 0
			price_without_discount = int(price_block.find('span', 'new-price').string.split()[0])

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

	def get_pagination_url_part(self):
		return '?&PAGEN_1='

	def get_product_link_from_product_card(self, product_card_html: BeautifulSoup) -> str:
		return product_card_html['href']