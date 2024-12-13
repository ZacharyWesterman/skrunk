import application.exceptions as exceptions
from application.db.weather import get_users, get_last_exec, get_alert_history, count_alert_history, get_weather_user, process_weather_user
from application.db import perms
from application.objects import Sorting
from . import query


@query.field('getWeatherUser')
@perms.module('weather')
def resolve_get_weather_user(_, info, username: str) -> dict:
	return {'__typename': 'WeatherUser', **process_weather_user(get_weather_user(username))}


@query.field('getWeatherUsers')
@perms.module('weather')
def resolve_get_weather_users(_, info) -> list:
	return get_users()


@query.field('getLastWeatherExec')
@perms.module('weather')
def resolve_get_last_execution(_, info) -> dict:
	return get_last_exec()  # May return None if weather alerts has never been run.


@query.field('weatherAlertHistory')
@perms.module('weather')
def resolve_get_alert_history(_, info, start: int, count: int) -> list:
	return get_alert_history(None, start, count)


@query.field('getWeatherAlerts')
@perms.module('weather')
@perms.require('admin', perform_on_self=True)
def resolve_get_weather_alerts(_, info, username: str, start: int, count: int) -> list:
	return get_alert_history(username, start, count)


@query.field('countWeatherAlerts')
@perms.module('weather')
@perms.require('admin', perform_on_self=True)
def resolve_count_weather_alerts(_, info, username: str) -> list:
	return count_alert_history(username)
