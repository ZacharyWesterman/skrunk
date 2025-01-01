"""application.scalars.color"""

__all__ = ['scalar']

from ariadne import ScalarType
import re
import application.exceptions as exceptions

scalar = ScalarType('Color')


@scalar.value_parser
def parse_color(value: str) -> str:
	match = re.match(r"^#[0-9a-fA-F]{6}$", value)

	if not match:
		raise exceptions.InvalidColor(value)

	return value
