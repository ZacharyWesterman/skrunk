__all__ = ['require']

from pymongo import MongoClient
import application.exceptions as exceptions
from application.tokens import decode_user_token

__mongo_url = 'mongodb://192.168.1.184:27017/'
db = MongoClient(__mongo_url)

def bad_creds() -> dict:
	return {
		'__typename': 'InsufficientCreds',
		'message': 'You are not qualified to perform this action.',
	}

def require(creds: list, *, perform_on_self: bool = True) -> callable:
	def inner(method: callable) -> callable:
		def wrap(_, info, *args, **kwargs):
			global db

			token = info.context.headers.get('Authorization', '').split(' ')
			if len(token) < 2:
				return bad_creds()

			username = decode_user_token(token[1]).get('username', '')

			# Unless otherwise specified,
			# Ignore credentials if user is editing their own data.
			if perform_on_self and 'username' in {**kwargs}:
				other_user = {**kwargs}.get('username')

				if other_user == username:
					return method(_, info, *args, **kwargs)

			# Make sure user has sufficient creds to perform this action
			userdata = db.data.users.find_one({'username': username})
			if not userdata:
				return bad_creds()

			# If user does not have ALL required creds, fail.
			if not all(k in userdata['creds'] for k in creds):
				return bad_creds()

			return method(_, info, *args, **kwargs)

		return wrap

	return inner
