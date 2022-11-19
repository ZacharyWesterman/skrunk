import application.exceptions as exceptions
from application.db.weather import create_user, delete_user

def resolve_create_weather_user(_, info, user_data: dict) -> dict:
	try:
		create_user(user_data)
		return { '__typename' : 'UserData', 'username': user_data['username'] }
	except exceptions.ClientError as e:
		return { '__typename' : 'BadUserNameError', 'message' : str(e) }

def resolve_delete_weather_user(_, info, username: str) -> dict:
	try:
		delete_user(username)
		return { '__typename' : 'UserData', 'username': username }
	except exceptions.UserDoesNotExistError as e:
		return { '__typename' : 'BadUserNameError', 'message' : str(e) }
