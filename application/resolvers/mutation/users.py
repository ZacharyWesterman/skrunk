import application.exceptions as exceptions
from application.db.users import create_user, get_user_data

def resolve_create_user(_, info, username: str, password: str) -> bool:
	try:
		create_user(username, password)
		return { '__typename' : 'UserData', **get_user_data(username) }
	except exceptions.ClientError as e:
		return { '__typename' : 'BadUserNameError', 'message' : str(e) }
