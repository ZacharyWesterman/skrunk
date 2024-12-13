from application.exceptions import ClientError
from typing import Callable


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
	def wrapper(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except ClientError as e:
			return {'__typename': e.__class__.__name__, 'message': str(e)}

	return wrapper
