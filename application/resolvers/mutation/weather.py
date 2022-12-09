import application.exceptions as exceptions
from application.db.weather import create_user, delete_user, set_user_excluded, update_user
import application.db.perms as perms

@perms.require(['admin'])
def resolve_create_weather_user(_, info, userdata: dict) -> dict:
	try:
		create_user(userdata)
		return { '__typename' : 'UserData', **userdata }
	except exceptions.ClientError as e:
		return { '__typename' : 'BadUserNameError', 'message' : str(e) }

@perms.require(['admin'], perform_on_self = False)
def resolve_delete_weather_user(_, info, username: str) -> dict:
	try:
		delete_user(username)
		return { '__typename' : 'UserData', 'username': username }
	except exceptions.UserDoesNotExistError as e:
		return { '__typename' : 'UserDoesNotExistError', 'message' : str(e) }

@perms.require(['admin'])
def resolve_enable_weather_user(_, info, username: str) -> dict:
	try:
		userdata = set_user_excluded(username, False)
		return { '__typename' : 'UserData', **userdata }
	except exceptions.UserDoesNotExistError as e:
		return { '__typename' : 'UserDoesNotExistError', 'message' : str(e) }

@perms.require(['admin'])
def resolve_disable_weather_user(_, info, username: str) -> dict:
	try:
		userdata = set_user_excluded(username, True)
		return { '__typename' : 'UserData', **userdata }
	except exceptions.UserDoesNotExistError as e:
		return { '__typename' : 'UserDoesNotExistError', 'message' : str(e) }

@perms.require(['admin'])
def resolve_update_weather_user(_, info, userdata: dict) -> dict:
	try:
		update_user(userdata)
		return { '__typename' : 'UserData', **userdata }
	except exceptions.UserDoesNotExistError as e:
		return { '__typename' : 'UserDoesNotExistError', 'message' : str(e) }
