import application.exceptions as exceptions
from application.db.weather import get_users, get_last_exec, get_alert_history, count_alert_history
from application.db import perms
from application.objects import Sorting

@perms.module('weather')
def resolve_get_weather_users(_, info) -> list:
	return get_users()

@perms.module('weather')
def resolve_get_last_execution(_, info) -> dict:
	return get_last_exec() #May return None if weather alerts has never been run.

@perms.module('weather')
def resolve_get_alert_history(_, info, start: int, count: int) -> list:
	return get_alert_history(None, start, count)

@perms.module('weather')
@perms.require('admin', perform_on_self = True)
def resolve_get_weather_alerts(_, info, username: str, start: int, count: int) -> list:
	return get_alert_history(username, start, count)

@perms.module('weather')
@perms.require('admin', perform_on_self = True)
def resolve_count_weather_alerts(_, info, username: str) -> list:
	return count_alert_history(username)
