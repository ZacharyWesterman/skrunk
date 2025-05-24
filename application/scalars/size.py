"""application.scalars.size"""

__all__ = ['scalar']

import re

from ariadne import ScalarType

import application.exceptions as exceptions

## Define a scalar type for size values
scalar = ScalarType('Size')


@scalar.value_parser
def parse_size(value: str) -> str:
	"""
	Parses a size string and validates its format.

	Args:
		value (str): The size string to be parsed. It should be a numeric value followed by a unit 
					 (%, px, em, rem, or in).

	Returns:
		str: The validated size string.

	Raises:
		exceptions.InvalidSize: If the size string does not match the expected format.
	"""
	match = re.match(r"^[0-9]+(%|px|r?em|in)$", value)

	if not match:
		raise exceptions.InvalidSize(value)

	return value
