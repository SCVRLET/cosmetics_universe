from typing import Union

from .base_parser import BaseParser

from .podrygka_parser import PodrygkaParser

from .randewoo_parser import RandewooParser

from .proficosmetics_parser import ProficosmeticsParser

from .ulybka_radugi_parser import UlybkaRadugiParser


class ParserGetter:
	def __init__(self):
		self._avail_parsers = {
			'podrygka': (PodrygkaParser(), 90),
			'randewoo': (RandewooParser(), 90),
			'proficosmetics': (ProficosmeticsParser(), 20),
			'ulybka_radugi': (UlybkaRadugiParser(), 20)
		}

	def get_parser(self, site_name: str) -> Union[BaseParser, None]:
		'''
			Возвращает объект для парсинга сайта по названию + оптимальное количество асинхронных запросов
		'''
		if site_name in self._avail_parsers.keys():
			return self._avail_parsers[site_name]
		else:
			return None