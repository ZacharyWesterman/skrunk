__all__ = ['scalar']

from datetime import datetime
from ariadne import ScalarType

scalar = ScalarType('Date')


@scalar.value_parser
def parse_date_value(value: str) -> str:
	return datetime.strptime(value, '%Y-%m-%d').strftime('%Y-%m-%d')
