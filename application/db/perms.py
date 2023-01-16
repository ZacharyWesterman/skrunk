__all__ = ['require']

import application.exceptions as exceptions
from application.tokens import decode_user_token

db = None

def bad_perms() -> dict:
	return {
		'__typename': 'InsufficientPerms',
		'message': 'You are not qualified to perform this action.',
	}

def caller_info(info) -> str:
	token = info.context.headers.get('Authorization', '').split(' ')
	if len(token) < 2:
		return None

	username = decode_user_token(token[1]).get('username')
	if username is None:
		return None

	userdata = db.find_one({'username': username})
	if not userdata:
		return None

	return userdata

def user_has_perms(user_data: dict, perm_list: list) -> bool:
	return all(k in user_data['perms'] for k in perm_list)

def satisfies(info, perms: list, data: dict, *, perform_on_self: bool = True) -> bool:
	# Make sure the user making the request exists
	user_data = caller_info(info)
	if user_data is None:
		return bad_perms()

	# Unless otherwise specified,
	# Ignore credentials if user is editing their own data.
	if perform_on_self:
		field = 'username' if 'username' in data else 'creator'
		other_user = data.get(field)

		if other_user is not None and (other_user == user_data.get('username') or other_user == str(user_data.get('_id'))):
			return True

	# If user does not have ALL required perms, fail.
	return user_has_perms(user_data, perms)

def require(perms: list, *, perform_on_self: bool = True) -> callable:
	def inner(method: callable) -> callable:
		def wrap(_, info, *args, **kwargs):
			if satisfies(info, perms, kwargs, perform_on_self = perform_on_self):
				return method(_, info, *args, **kwargs)
			else:
				return bad_perms()

		return wrap

	return inner
