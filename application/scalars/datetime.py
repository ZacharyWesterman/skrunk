"""application.scalars.datetime"""

__all__ = ['scalar']

from datetime import datetime
from ariadne import ScalarType

## Define a scalar type for datetime
scalar = ScalarType('DateTime')

# @scalar.serializer
# def serialize_datetime(value: datetime) -> str:
# 	return value.strftime('%Y-%m-%d %H:%M:%S')


@scalar.value_parser
def parse_datetime_value(value: str) -> datetime:
	"""
	Parses a datetime string into a datetime object.

	Args:
		value (str): The datetime string to parse. Expected format is '%Y-%m-%d %H:%M:%S'.

	Returns:
		datetime: A datetime object representing the parsed date and time.

	Raises:
		ValueError: If the input string does not match the expected format.
	"""
	return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
