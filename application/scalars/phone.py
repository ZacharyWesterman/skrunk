"""application.scalars.phone"""

__all__ = ['scalar']

import re

from ariadne import ScalarType

import application.exceptions as exceptions

## Define a scalar type for phone numbers
scalar = ScalarType('PhoneNumber')


@scalar.value_parser
def parse_phone(value: str) -> str:
	"""
	Parses a phone number string by removing all non-numeric characters and 
	ensuring it is exactly 10 digits long.

	Args:
		value (str): The phone number string to be parsed.

	Returns:
		str: The cleaned phone number string containing only digits.

	Raises:
		exceptions.InvalidPhone: If the cleaned phone number is not exactly 10 digits long.
	"""
	value = re.sub('[^0-9]', '', value)
	if len(value) != 10:
		raise exceptions.InvalidPhone

	return value
