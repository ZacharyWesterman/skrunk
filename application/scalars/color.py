__all__ = ['scalar']

from ariadne import ScalarType
import re

scalar = ScalarType('Color')

@scalar.value_parser
def parse_color(value: str) -> str:
	match = re.match(r"^#[0-9a-fA-F]{6}$", value)

	if not match:
		raise ValueError(f'The string "{value}" is not a 7-character hex color.')

	return value
