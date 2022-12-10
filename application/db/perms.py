__all__ = ['require']

import application.exceptions as exceptions
from application.tokens import decode_user_token

db = None

def bad_perms() -> dict:
	return {
		'__typename': 'InsufficientPerms',
		'message': 'You are not qualified to perform this action.',
	}

def require(perms: list, *, perform_on_self: bool = True) -> callable:
	def inner(method: callable) -> callable:
		def wrap(_, info, *args, **kwargs):
			global db

			token = info.context.headers.get('Authorization', '').split(' ')
			if len(token) < 2:
				return bad_perms()

			username = decode_user_token(token[1]).get('username', '')

			# Unless otherwise specified,
			# Ignore credentials if user is editing their own data.
			if perform_on_self and 'username' in {**kwargs}:
				other_user = {**kwargs}.get('username')

				if other_user == username:
					return method(_, info, *args, **kwargs)

			# Make sure user has sufficient perms to perform this action
			userdata = db.data.users.find_one({'username': username})
			if not userdata:
				return bad_perms()

			# If user does not have ALL required perms, fail.
			if not all(k in userdata['perms'] for k in perms):
				return bad_perms()

			return method(_, info, *args, **kwargs)

		return wrap

	return inner
