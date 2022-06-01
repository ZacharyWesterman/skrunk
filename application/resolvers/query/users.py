import application.exceptions as exceptions
from application.db.users import get_user_data, create_user_token

import bcrypt

def resolve_get_user(_, info, username: str) -> dict:
	try:
		return { '__typename': 'UserData', **get_user_data(username), 'password': None }
	except exceptions.ClientError as e:
		return { '__typename': type(e).__name__, 'message': str(e) }

def resolve_authenticate(_, info, username: str, password: str) -> str:
	try:
		userdata = get_user_data(username)

		if not bcrypt.checkpw(password.encode('utf-8'), userdata.get('password').encode('utf-8')):
			raise exceptions.AuthenticationError(f'Authentication failed')

		login_token = create_user_token(username)

		return { '__typename': 'AuthToken', 'token': login_token }
	except exceptions.ClientError as e:
		return { '__typename': type(e).__name__, 'message': str(e) }
