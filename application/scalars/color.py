"""application.scalars.color"""

__all__ = ['scalar']

from ariadne import ScalarType
import re
import application.exceptions as exceptions

## Define a scalar type for color values
scalar = ScalarType('Color')


@scalar.value_parser
def parse_color(value: str) -> str:
	"""
	Parses a string to ensure it is a valid hexadecimal color code.

	Args:
		value (str): The string to be validated as a hexadecimal color code.

	Returns:
		str: The validated hexadecimal color code.

	Raises:
		exceptions.InvalidColor: If the input string is not a valid hexadecimal color code.
	"""
	match = re.match(r"^#[0-9a-fA-F]{6}$", value)

	if not match:
		raise exceptions.InvalidColor(value)

	return value
