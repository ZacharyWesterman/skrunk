"""
This module provides logic for checking user permissions and ownership of data.
Permissions are a big part of the application, allowing users to only perform actions
they are allowed to, based on their roles and the data they are interacting with.

Likewise, it provides a way to check if the user has access to specific modules (features)
within the application. Unlike permissions which are per-user, modules can be managed
server-wide, per group, or per user.

Resolvers can use the `require` and `require_all` decorators to enforce
permissions on the calling user before executing the resolver function,
and the `module` decorator to check if the user has access to specific modules.
"""

from inspect import getfullargspec
from typing import Any, Callable

from pymongo.collection import Collection

from application import exceptions, tokens
from application.db import users

## A pointer to the API key database collection.
apikeydb: Collection = None  # type: ignore[assignment]


def bad_perms() -> dict[str, str]:
	"""
	Returns a dictionary representing an insufficient permissions error.

	Returns:
		dict[str, str]: A dictionary containing the error type and message indicating
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
		dict[str, Any] | None: The user data associated with the username if available,
			otherwise the API key information if the token is an API key.
			Returns None if neither is found or an error occurs during retrieval.
	"""
	tok = tokens.get_request_token()
	if not tok:
		return None

	try:
		username = tokens.decode_user_token(tok).get('username')
	except exceptions.InvalidJWTError:
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
		dict[str, Any]: The user data associated with the username if available,
			otherwise the API key information if the token is an API key.

	Raises:
		exceptions.AuthenticationError: If the token is invalid or the user does not exist.
		exceptions.UserDoesNotExistError: If the user does not exist in the database.
	"""
	tok = tokens.get_request_token()
	if not tok:
		raise exceptions.AuthenticationError()

	try:
		username = tokens.decode_user_token(tok).get('username')
	except exceptions.InvalidJWTError as e:
		apikey: dict | None = apikeydb.find_one({'key': tok})
		if apikey is None:
			raise exceptions.AuthenticationError() from e

		return apikey

	if username is None:
		raise exceptions.AuthenticationError()

	return users.get_user_data(username)


def user_has_perms(user_data: dict, perm_list: tuple[str, ...]) -> bool:
	"""
	Check if the user has any of the specified permissions.

	Args:
		user_data (dict): A dictionary containing user information,
			including a 'perms' key with a list of permissions.
		perm_list (list): A list of permissions to check against the user's permissions.

	Returns:
		bool: True if the user has any of the specified permissions, False otherwise.
	"""
	return any(k in user_data['perms'] for k in perm_list)


def satisfies(
    perms: tuple[str, ...],
    data: dict | None = None,
    *,
	perform_on_self: bool | tuple[bool, ...] = False,
    data_func: Callable | None = None
) -> bool | dict:
	"""Check if the calling user has any of the given permissions.

	Args:
		perms (list[str]): The permissions that must have at least 1 satisfied.
		perform_on_self (bool | tuple[bool, ...]): If True, permissions will be ignored when
			the user is editing their own data.
		data_func (Callable|None): If specified, this function will give the
			data to be checked for ownership. Otherwise, the main function's parameters are checked.

	Returns:
		bool | dict: True if the user has all required permissions, or if perform_on_self is True
			AND the data being operated on belongs to the user.
			If the user does not have the required permissions,
			returns a dictionary representing an insufficient permissions error.
			Otherwise, returns False.
	"""

	# Make sure the user making the request exists
	user_data = caller_info()
	if user_data is None:
		return bad_perms()

	if data is None:
		data = {}

	if isinstance(perform_on_self, bool):
		# If perform_on_self is a bool, convert it to a tuple for consistency.
		perform_on_self = (perform_on_self,)

	if isinstance(perform_on_self, tuple) and len(perform_on_self) < len(perms):
		# if the tuple is shorter than the number of permissions,
		# append False for the remaining permissions.
		perform_on_self = perform_on_self + (False,) * (len(perms) - len(perform_on_self))

	# Unless otherwise specified,
	# Ignore credentials if user is editing their own data.
	if 'username' in user_data and True in perform_on_self:
		for i in range(len(perms)):
			if perform_on_self[i]:
				self_data = data
				if data_func is not None:
					spec = getfullargspec(data_func)
					args = dict((i, data[i]) for i in spec[0] + spec[4] if i in data)
					self_data = data_func(**args)

				if not isinstance(self_data, dict):
					return bad_perms()

				fields = [i for i in ['owner', 'creator', 'username'] if i in self_data]
				other_user = str(self_data.get(fields[0])) if len(fields) else None

				if other_user is not None and (
					other_user == user_data.get('username') or
					other_user == str(user_data.get('_id'))
				):
					return True

	# If user does not have ALL required perms, fail.
	return user_has_perms(user_data, perms)


def require(
    *perms: str,
    perform_on_self: bool | tuple[bool, ...] = False,
    data_func: Callable | None = None
) -> Callable:
	"""Require the calling user to have any of the specified permissions.

	This is a decorator for application resolvers,
	to avoid redundant permission-checking logic all over the place.
	If the permissions are not satisfied when the resolver is called, 
	then the resolver will be overridden and will instead return a bad_perms() dict.

	Args:
		*perms (str): The permissions that must have at least 1 satisfied.
		perform_on_self (bool | tuple[bool, ...]): If True, permissions will be ignored
			when the user is editing their own data.
		data_func (Callable|None): If specified, this function will give
			the data to be checked for ownership. Otherwise, the main function's
			parameters are checked.

	Returns:
		Callable: The resolver function, with decorator applied.
	"""

	def inner(method: Callable) -> Callable:
		def wrap(_, info, *args, **kwargs):
			if satisfies(perms, kwargs, perform_on_self=perform_on_self, data_func=data_func):
				return method(_, info, *args, **kwargs)

			return bad_perms()

		return wrap

	return inner


def require_all(
    *perms: str,
    perform_on_self: bool | tuple[bool, ...] = False,
    data_func: Callable | None = None
) -> Callable:
	"""Require the calling user to have all of the specified permissions.

	This is a decorator for application resolvers,
	to avoid redundant permission-checking logic all over the place.
	If the permissions are not satisfied when the resolver is called, 
	then the resolver will be overridden and will instead return a bad_perms() dict.

	Args:
		*perms (str): The permissions that must all be satisfied.
		perform_on_self (bool | tuple[bool, ...]): If True, permissions will be ignored
			when the user is editing their own data.
		data_func (Callable|None): If specified, this function will give
			the data to be checked for ownership. Otherwise, the main function's
			parameters are checked.

	Returns:
		Callable: The resolver function, with decorator applied.
	"""

	def inner(method: Callable) -> Callable:
		def wrap(_, info, *args, **kwargs):
			if not satisfies(perms, kwargs, perform_on_self=perform_on_self, data_func=data_func):
				return bad_perms()

			return method(_, info, *args, **kwargs)

		return wrap

	return inner


def module(*modules: str) -> Callable:
	"""Require the calling user to have all the specified modules enabled.

	This is a decorator for application resolvers,
	to avoid redundant module-checking logic all over the place.
	If the user does not have one or more of the specified modules enabled 
	when the resolver is called, then the resolver will be overridden and 
	will instead return a bad_perms() dict.

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

			return method(_, info, *args, **kwargs)

		return wrap

	return inner
