__all__ = ['require']

from application import tokens
from inspect import getfullargspec

db = None

def bad_perms() -> dict:
	return {
		'__typename': 'InsufficientPerms',
		'message': 'You are not allowed to perform this action.',
	}

def caller_info() -> str:
	username = tokens.decode_user_token(tokens.get_request_token()).get('username')
	if username is None:
		return None

	userdata = db.find_one({'username': username})
	if not userdata:
		return None

	return userdata

def user_has_perms(user_data: dict, perm_list: list) -> bool:
	return all(k in user_data['perms'] for k in perm_list)

def satisfies(perms: list, data: dict = {}, *, perform_on_self: bool = True, data_func: callable = None) -> bool:
	"""Check if the calling user has certain permissions.

	### Parameters:
	@perms: The permissions that must ALL be satisfied.
	@perform_on_self: If True, permissions will be ignored when the user is editing their own data.
	@data_func: If specified, this function will give the data to be checked for ownership. Otherwise, the main function's parameters are checked.

	### Returns:
	- True if the user has all required permissions, or if perform_on_self is True AND the data being operated on belongs to the user.
	"""

	# Make sure the user making the request exists
	user_data = caller_info()
	if user_data is None:
		return bad_perms()

	# Unless otherwise specified,
	# Ignore credentials if user is editing their own data.
	if perform_on_self:
		if data_func is not None:
			spec = getfullargspec(data_func)
			args = dict((i, data[i]) for i in spec[0] + spec[4] if i in data)
			data = data_func(**args)

		fields = [i for i in ['owner', 'creator', 'username'] if i in data]
		other_user = str(data.get(fields[0])) if len(fields) else None

		if other_user is not None and (other_user == user_data.get('username') or other_user == str(user_data.get('_id'))):
			return True

	# If user does not have ALL required perms, fail.
	return user_has_perms(user_data, perms)

def require(perms: list[str], *, perform_on_self: bool = False, data_func: callable = None) -> callable:
	"""Require the calling user to have certain permissions.

	This is a decorator for application resolvers, to avoid redundant permission-checking logic all over the place.
	If the permissions are not satisfied when the resolver is called, then the resolver will be overridden and will instead return a bad_perms() dict.

	### Parameters:
	@perms: The permissions that must ALL be satisfied.
	@perform_on_self: If True, permissions will be ignored when the user is editing their own data.
	@data_func: If specified, this function will give the data to be checked for ownership. Otherwise, the main function's parameters are checked.

	### Returns:
	- The resolver function, with decorator applied.
	"""

	def inner(method: callable) -> callable:
		def wrap(_, info, *args, **kwargs):
			if satisfies(perms, kwargs, perform_on_self = perform_on_self, data_func = data_func):
				return method(_, info, *args, **kwargs)
			else:
				return bad_perms()

		return wrap

	return inner
