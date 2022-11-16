import application.exceptions as exceptions
from application.db.users import get_user_data

def resolve_get_user(_, info, username: str) -> dict:
	try:
		return { '__typename': 'UserData', **get_user_data(username) }
	except exceptions.ClientError as e:
		return { '__typename': 'UserDoesNotExistError', 'message': str(e) }
