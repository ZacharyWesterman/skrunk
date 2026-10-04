"""application.resolvers.decorators"""

from typing import Callable

from application.exceptions import ClientError


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


def typed(func: Callable) -> Callable:
	"""
	Decorator that automatically injects the '__typename' field when returning dicts
	that don't already have the field, based on function type hints.

	Note that this decorator must be the first in any decorator chain, that is
	there may not be any decorators between this and the actual function.

	Args:
		func (Callable): The function to be wrapped by the decorator.

	Returns:
		Callable: A wrapped function that injects the `__typename` field into the result.
	"""

	def wrapper(*args, **kwargs):
		result = func(*args, **kwargs)

		if (
			isinstance(result, dict) and
			'__typename' not in result and
			'return' in func.__annotations__
		):
			retn_type = func.__annotations__['return']
			if not isinstance(retn_type, str):
				retn_type = retn_type.__name__

			return {
				'__typename': retn_type,
				**result,
			}
		return result

	return wrapper
