import re

from bs4 import BeautifulSoup

from .base_parser import BaseParser


class ProficosmeticsParser(BaseParser):
	def _get_product_size(self, product_name: str) -> str:
		return ' '.join(product_name.split()[-2:])

	def _get_product_description(self, product_page_html: BeautifulSoup) -> str:
		return product_page_html.find('div', class_='kr_text text pad_bottom_container pad_bottom_container_last').find('p').text

	def _get_product_brand(self, product_page_html: BeautifulSoup) -> str:
		brand_block = product_page_html.find('div', class_='product_main_desc').find('h4')

		if brand_block:
			return brand_block.find('span').text

		return 'Неизвестно'

	def _get_product_name(self, product_page_html: BeautifulSoup) -> str:
		return product_page_html.find('div', class_='product_main').find('div', itemprop='name').text

	def _get_product_img_link(self, product_page_html: BeautifulSoup) -> str:
		return product_page_html.find('div', class_='product_preview_slider').find('div', class_='slide').find('a')['href']

	def _is_product_available(self, product_page_html: BeautifulSoup) -> bool:
		return bool(product_page_html.find('div', class_='product_main_desc').find('div', class_='product_popup'))

	def is_product_available_from_product_card(self, product_card_html: BeautifulSoup) -> bool:
		return True

	def _get_offer_size(self, offer_block_html: BeautifulSoup) -> str:
		col_2_text = offer_block_html.find('div', class_='col-2').text

		pattern = 	r'(\d+)\s?((гр)|(кг)|(мл)|(л))'
		match = re.search(pattern, col_2_text)

		return f'{match.group(1)} {match.group(2)}' if match else ''

	def get_product_cards_from_catalog_page(self, catalog_page_html: str) -> list:
		soup = BeautifulSoup(catalog_page_html, 'html.parser')

		return soup.find_all('li', itemtype='http://schema.org/Product')

	def _is_offer_available(self, offer: BeautifulSoup) -> bool:
		return True

	def get_number_of_pages_in_catalog(self, catalog_page_html: str) -> int:
		soup = BeautifulSoup(catalog_page_html, 'html.parser')

		pag_block = soup.find('div', class_='pager')

		if pag_block:
			last_page_button = pag_block.find_all('a')[-2]

			page_last_number = int(last_page_button.text)

			return page_last_number

		return 1

	def get_info_from_product_page(self, product_page_html: str):
		soup = BeautifulSoup(product_page_html, 'html.parser')

		product_name = self._get_product_name(soup)
		product_image_link = self._get_product_img_link(soup)

		offers = []

		product_types = soup.find('div', class_='kr_variants')

		if product_types:
			for offer in product_types.find_all('li'):
				offer_info = {}

				size = self._get_offer_size(offer)
				is_available = self._is_offer_available(offer)

				offer_info.update({'size': size, 'is_available': is_available, 'price_without_discount': 0, 'discount': 0})

				price_without_discount_text = offer.find('div', class_='col-2').find('strong').text.split('a')[0]
				price_without_discount = int(price_without_discount_text.replace('\xa0', ''))

				offer_info.update({'price_without_discount': price_without_discount})

				offers.append(offer_info) 

		else:
			size = self._get_product_size(product_name)
			price_block = soup.find('div', class_='buy_desc')

			is_available = self._is_product_available(soup)

			offer_info = {'size': size, 'is_available': is_available, 'price_without_discount': 0, 'discount': 0}

			price_without_discount = int(price_block.find('p', class_='new_price').text.split('a')[0].replace('\xa0', ''))

			offer_info.update({'price_without_discount': price_without_discount})

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
		return '/p'

	def get_product_link_from_product_card(self, product_card_html: BeautifulSoup) -> str:
		return product_card_html.find('p', class_='product_name').find('a')['href']