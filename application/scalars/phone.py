__all__ = ['scalar']

from ariadne import ScalarType
import re
import application.exceptions as exceptions

scalar = ScalarType('PhoneNumber')

@scalar.value_parser
def parse_phone(value: str) -> str:
	value = re.sub('[^0-9]', '', value)
	if len(value) != 10:
		raise exceptions.InvalidPhone

	return value
