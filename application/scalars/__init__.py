from datetime import datetime
from ariadne import ScalarType
import re

datetime_scalar = ScalarType('DateTime')
phone_scalar = ScalarType('PhoneNumber')

@datetime_scalar.serializer
def serialize_datetime(value: datetime) -> str:
	return value.strftime('%Y-%m-%d %H:%M:%S')

@datetime_scalar.value_parser
def parse_datetime_value(value: str) -> datetime:
	return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

@phone_scalar.value_parser
def parse_phone(value: str) -> str:
	value = re.sub('[^0-9]', '', value)
	if len(value) != 10:
		raise ValueError('Phone number must be 10 digits exactly.')

	return value

scalars = [phone_scalar, datetime_scalar]
