
from tag_query import exceptions


def boolean(name: str, value: str) -> bool:
	val = {
		'true': True,
		'false': False,
		'1': True,
		'0': False,
	}.get(value.lower())

	if val is None:
		raise exceptions.InvalidFieldValue(name)

	return val
