from typing import Union

from .base_parser import BaseParser

from .podrygka_parser import PodrygkaParser

from .randewoo_parser import RandewooParser


class ParserGetter:
	def __init__(self):
		self._avail_parsers = {
			'podrygka': PodrygkaParser(),
			'randewoo': RandewooParser(),
		}

	def get_parser(self, site_name: str) -> Union[BaseParser, None]:
		if site_name in self._avail_parsers.keys():
			return self._avail_parsers[site_name]
		else:
			return None