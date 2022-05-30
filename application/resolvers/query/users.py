import application.exceptions as exceptions
from application.db.users import get_user_data

def resolve_get_user(_, info, username: str) -> dict:
	try:
		return { '__typename': 'UserData', 'username':username }
	except exceptions.ClientError as e:
		return { '__typename': type(e).__name__, 'message': str(e) }

def resolve_authenticate(_, info, username: str, password: str) -> str:
	try:
		userdata = get_user_data(username)
		if password != userdata.get('password'):
			raise exceptions.AuthenticationError(f'Authentication failed')

		return { '__typename': 'AuthToken', 'token': 'sample_token'}
	except exceptions.ClientError as e:
		return { '__typename': type(e).__name__, 'message': str(e) }
