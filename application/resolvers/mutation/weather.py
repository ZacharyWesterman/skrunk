from application.db.weather import create_user, delete_user, set_user_excluded, update_user
import application.db.perms as perms
from ..decorators import *

@perms.require('weather')
@perms.require(['admin'], perform_on_self = True)
@handle_client_exceptions
def resolve_create_weather_user(_, info, userdata: dict) -> dict:
	create_user(userdata)
	return { '__typename' : 'UserData', **userdata }

@perms.require('weather')
@perms.require(['admin'])
@handle_client_exceptions
def resolve_delete_weather_user(_, info, username: str) -> dict:
	delete_user(username)
	return { '__typename' : 'UserData', 'username': username }

@perms.require('weather')
@perms.require(['admin'], perform_on_self = True)
@handle_client_exceptions
def resolve_enable_weather_user(_, info, username: str) -> dict:
	userdata = set_user_excluded(username, False)
	return { '__typename' : 'UserData', **userdata }

@perms.require('weather')
@perms.require(['admin'], perform_on_self = True)
@handle_client_exceptions
def resolve_disable_weather_user(_, info, username: str) -> dict:
	userdata = set_user_excluded(username, True)
	return { '__typename' : 'UserData', **userdata }

@perms.require('weather')
@handle_client_exceptions
def resolve_update_weather_user(_, info, userdata: dict) -> dict:
	if not perms.satisfies(['edit']) and not perms.satisfies(['admin'], userdata, perform_on_self = True):
		return perms.bad_perms()

	update_user(userdata)
	return { '__typename' : 'UserData', **userdata }
