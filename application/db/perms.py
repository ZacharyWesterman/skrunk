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

	userdata = db.data.users.find_one({'username': username})
	if not userdata:
		return None

	return userdata

def user_has_perms(user_data: dict, perm_list: list) -> bool:
	return all(k in user_data['perms'] for k in perm_list)

def require(perms: list, *, perform_on_self: bool = True) -> callable:
	def inner(method: callable) -> callable:
		def wrap(_, info, *args, **kwargs):
			global db

			# Make sure the user making the request exists
			user_data = caller_info(info)
			if user_data is None:
				return bad_perms()

			# Unless otherwise specified,
			# Ignore credentials if user is editing their own data.
			if perform_on_self and 'username' in {**kwargs}:
				other_user = {**kwargs}.get('username')

				if other_user == user_data['username']:
					return method(_, info, *args, **kwargs)

			# If user does not have ALL required perms, fail.
			if not user_has_perms(user_data, perms):
				return bad_perms()

			return method(_, info, *args, **kwargs)

		return wrap

	return inner
