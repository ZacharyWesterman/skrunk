__all__ = ['scalar']

from ariadne import ScalarType
import re
import application.exceptions as exceptions

scalar = ScalarType('Size')


@scalar.value_parser
def parse_size(value: str) -> str:
	match = re.match(r"^[0-9]+(%|px|r?em|in)$", value)

	if not match:
		raise exceptions.InvalidSize(value)

	return value
