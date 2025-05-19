"""application.db.perms"""

__all__ = ['require']

from application import tokens, exceptions
from inspect import getfullargspec
from application.db import users
from typing import Callable, Any

from pymongo.collection import Collection

## A pointer to the API key database collection.
apikeydb: Collection = None  # type: ignore[assignment]


def bad_perms() -> dict:
	"""
	Returns a dictionary representing an insufficient permissions error.

	Returns:
		dict: A dictionary containing the error type and message indicating
			  that the user is not allowed to perform the requested action.
	"""
	return {
		'__typename': 'InsufficientPerms',
		'message': 'You are not allowed to perform this action.',
	}


def caller_info() -> dict[str, Any] | None:
	"""
	Retrieves caller information based on the request token.

	The function attempts to decode the request token to extract the username.
	If decoding fails, it treats the token as an API key and retrieves the corresponding
	API key information from the database.

	Returns:
		str: The user data associated with the username if available, otherwise the API key
			 information if the token is an API key. Returns None if neither is found or an
			 error occurs during retrieval.
	"""
	tok = tokens.get_request_token()
	if not tok:
		return None

	try:
		username = tokens.decode_user_token(tok).get('username')
	except:
		apikey = apikeydb.find_one({'key': tok})
		if apikey is None:
			return None
		apikey['username'] = f'API: {apikey["description"]}'
		return apikey

	if username is None:
		return None

	try:
		return users.get_user_data(username)
	except exceptions.ClientError:
		return None


def caller_info_strict() -> dict[str, Any]:
	"""
	Retrieves caller information based on the request token.

	The function attempts to decode the request token to extract the username.
	If decoding fails, it treats the token as an API key and retrieves the corresponding
	API key information from the database.

	Returns:
		str: The user data associated with the username if available, otherwise the API key
			 information if the token is an API key.

	Raises:
		exceptions.AuthenticationError: If the token is invalid or the user does not exist.
		exceptions.UserDoesNotExistError: If the user does not exist in the database.
	"""
	tok = tokens.get_request_token()
	if not tok:
		raise exceptions.AuthenticationError()

	try:
		username = tokens.decode_user_token(tok).get('username')
	except:
		apikey: dict | None = apikeydb.find_one({'key': tok})
		if apikey is None:
			raise exceptions.AuthenticationError()

		return apikey

	if username is None:
		raise exceptions.AuthenticationError()

	return users.get_user_data(username)


def user_has_perms(user_data: dict, perm_list: tuple[str, ...]) -> bool:
	"""
	Check if the user has any of the specified permissions.

	Args:
		user_data (dict): A dictionary containing user information, including a 'perms' key with a list of permissions.
		perm_list (list): A list of permissions to check against the user's permissions.

	Returns:
		bool: True if the user has any of the specified permissions, False otherwise.
	"""
	return any(k in user_data['perms'] for k in perm_list)


def satisfies(perms: tuple[str, ...], data: dict = {}, *, perform_on_self: bool = False, data_func: Callable | None = None) -> bool | dict:
	"""Check if the calling user has any of the given permissions.

	Args:
		perms (list[str]): The permissions that must have at least 1 satisfied.
		perform_on_self (bool): If True, permissions will be ignored when the user is editing their own data.
		data_func (Callable|None): If specified, this function will give the data to be checked for ownership. Otherwise, the main function's parameters are checked.

	Returns:
		bool: True if the user has all required permissions, or if perform_on_self is True AND the data being operated on belongs to the user.
	"""

	# Make sure the user making the request exists
	user_data = caller_info()
	if user_data is None:
		return bad_perms()

	# Unless otherwise specified,
	# Ignore credentials if user is editing their own data.
	if perform_on_self and 'username' in user_data:
		if data_func is not None:
			spec = getfullargspec(data_func)
			args = dict((i, data[i]) for i in spec[0] + spec[4] if i in data)
			data = data_func(**args)

		if type(data) is not dict:
			return bad_perms()

		fields = [i for i in ['owner', 'creator', 'username'] if i in data]
		other_user = str(data.get(fields[0])) if len(fields) else None

		if other_user is not None and (other_user == user_data.get('username') or other_user == str(user_data.get('_id'))):
			return True

	# If user does not have ALL required perms, fail.
	return user_has_perms(user_data, perms)


def require(*perms: str, perform_on_self: bool = False, data_func: Callable | None = None) -> Callable:
	"""Require the calling user to have any of the specified permissions.

	This is a decorator for application resolvers, to avoid redundant permission-checking logic all over the place.
	If the permissions are not satisfied when the resolver is called, then the resolver will be overridden and will instead return a bad_perms() dict.

	Args:
		*perms (str): The permissions that must have at least 1 satisfied.
		perform_on_self (bool): If True, permissions will be ignored when the user is editing their own data.
		data_func (Callable|None): If specified, this function will give the data to be checked for ownership. Otherwise, the main function's parameters are checked.

	Returns:
		Callable: The resolver function, with decorator applied.
	"""

	def inner(method: Callable) -> Callable:
		def wrap(_, info, *args, **kwargs):
			if satisfies(perms, kwargs, perform_on_self=perform_on_self, data_func=data_func):
				return method(_, info, *args, **kwargs)
			else:
				return bad_perms()

		return wrap

	return inner


def module(*modules: str) -> Callable:
	"""Require the calling user to have all the specified modules enabled.

	This is a decorator for application resolvers, to avoid redundant module-checking logic all over the place.
	If the user does not have one or more of the specified modules enabled when the resolver is called, then the resolver will be overridden and will instead return a bad_perms() dict.

	Args:
		modules (list[str]): The modules that must ALL be enabled for the user.

	Returns:
		Callable: The resolver function, with decorator applied.
	"""

	def inner(method: Callable) -> Callable:
		def wrap(_, info, *args, **kwargs):
			user_data = caller_info()

			# If module(s) are disabled for the user, return error.
			if user_data is None or set(user_data.get('disabled_modules', [])).intersection(modules):
				return bad_perms()
			else:
				return method(_, info, *args, **kwargs)

		return wrap

	return inner
