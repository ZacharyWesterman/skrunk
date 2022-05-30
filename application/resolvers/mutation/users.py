import application.exceptions as exceptions
from application.db.users import get_user_data, update_user_token

import secrets, bcrypt

def resolve_authenticate(_, info, username: str, password: str) -> str:
	try:
		userdata = get_user_data(username)

		if not bcrypt.checkpw(password.encode('utf-8'), userdata.get('password').encode('utf-8')):
			raise exceptions.AuthenticationError(f'Authentication failed')

		login_token = secrets.token_urlsafe()
		update_user_token(username, login_token)

		return { '__typename': 'AuthToken', 'token': login_token }
	except exceptions.ClientError as e:
		return { '__typename': type(e).__name__, 'message': str(e) }
