__all__ = ['scalar']

from datetime import datetime
from ariadne import ScalarType

scalar = ScalarType('DateTime')

# @datetime_scalar.serializer
# def serialize_datetime(value: datetime) -> str:
# 	return value.strftime('%Y-%m-%d %H:%M:%S')

@scalar.value_parser
def parse_datetime_value(value: str) -> datetime:
	return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
