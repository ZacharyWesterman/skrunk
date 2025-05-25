"""application.resolvers.query.weather"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.weather import (count_alert_history, get_alert_history,
                                    get_last_exec, get_users, get_weather_user,
                                    process_weather_user)

from . import query


@query.field('getWeatherUser')
@perms.module('weather')
def resolve_get_weather_user(_, _info: GraphQLResolveInfo, username: str) -> dict:
	return {'__typename': 'WeatherUser', **process_weather_user(get_weather_user(username))}


@query.field('getWeatherUsers')
@perms.module('weather')
def resolve_get_weather_users(_, _info: GraphQLResolveInfo) -> list:
	return get_users()


@query.field('getLastWeatherExec')
@perms.module('weather')
def resolve_get_last_execution(_, _info: GraphQLResolveInfo) -> dict | None:
	return get_last_exec()  # May return None if weather alerts has never been run.


@query.field('weatherAlertHistory')
@perms.module('weather')
def resolve_get_alert_history(_, _info: GraphQLResolveInfo, start: int, count: int) -> list:
	return get_alert_history(None, start, count)


@query.field('getWeatherAlerts')
@perms.module('weather')
@perms.require('admin', perform_on_self=True)
def resolve_get_weather_alerts(_, _info: GraphQLResolveInfo, username: str, start: int, count: int) -> list:
	return get_alert_history(username, start, count)


@query.field('countWeatherAlerts')
@perms.module('weather')
@perms.require('admin', perform_on_self=True)
def resolve_count_weather_alerts(_, _info: GraphQLResolveInfo, username: str) -> int:
	return count_alert_history(username)
