"""application.scalars.date"""

__all__ = ['scalar']

from datetime import datetime

from ariadne import ScalarType

## Define a scalar type for date values
scalar = ScalarType('Date')


@scalar.value_parser
def parse_date_value(value: str) -> str:
	"""
	Parses a date string in the format 'YYYY-MM-DD' and returns it in the same format.

	Args:
		value (str): The date string to be parsed.

	Returns:
		str: The parsed date string in the format 'YYYY-MM-DD'.
	"""
	return datetime.strptime(value, '%Y-%m-%d').strftime('%Y-%m-%d')
