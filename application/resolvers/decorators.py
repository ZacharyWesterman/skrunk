from application.exceptions import ClientError
from typing import Callable
from dataclasses import is_dataclass, asdict

def handle_client_exceptions(func: Callable) -> Callable:
	"""
	Decorator that handles client-specific exceptions and returns 
	error details to the client without crashing the application.

	This decorator captures exceptions of type `ClientError` that occur 
	within the decorated function and returns a structured error response 
	containing the exception type and message.

	Args:
		func (Callable): The function to be wrapped by the decorator.

	Returns:
		Callable: A wrapped function that handles `ClientError` exceptions.
	"""

	def dictify(obj):
		if type(obj) is list:
			return [dictify(i) for i in obj]
		if type(obj) is dict:
			return {key: dictify(val) for key, val in obj}
		if is_dataclass(obj):
			return { '__typename': obj.__class__.__name__, **asdict(obj) }

		return obj

	def wrapper(*args, **kwargs):
		try:
			return dictify(func(*args, **kwargs))
		except ClientError as e:
			return { '__typename': e.__class__.__name__, 'message': str(e) }

	return wrapper
