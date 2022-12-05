__all__ = ['scalar']

from ariadne import ScalarType
import re

scalar = ScalarType('PhoneNumber')

@scalar.value_parser
def parse_phone(value: str) -> str:
	value = re.sub('[^0-9]', '', value)
	if len(value) != 10:
		raise ValueError('Phone number must be 10 digits exactly.')

	return value
