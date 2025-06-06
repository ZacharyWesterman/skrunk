"""application.resolvers.mutation.weather"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.weather import (create_user, delete_user,
                                    log_user_weather_alert, log_weather_alert,
                                    set_user_excluded, update_user)

from ..decorators import handle_client_exceptions
from . import mutation


@mutation.field('createWeatherUser')
@perms.module('weather')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_create_weather_user(_, _info: GraphQLResolveInfo, userdata: dict) -> dict:
	return {'__typename': 'WeatherUser', **create_user(userdata)}


@mutation.field('deleteWeatherUser')
@perms.module('weather')
@perms.require('admin')
@handle_client_exceptions
def resolve_delete_weather_user(_, _info: GraphQLResolveInfo, username: str) -> dict:
	return {'__typename': 'WeatherUser', **delete_user(username)}


@mutation.field('enableWeatherUser')
@perms.module('weather')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_enable_weather_user(_, _info: GraphQLResolveInfo, username: str) -> dict:
	return {'__typename': 'WeatherUser', **set_user_excluded(username, False)}


@mutation.field('disableWeatherUser')
@perms.module('weather')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_disable_weather_user(_, _info: GraphQLResolveInfo, username: str) -> dict:
	userdata = set_user_excluded(username, True)
	return {'__typename': 'WeatherUser', **userdata}


@mutation.field('updateWeatherUser')
@perms.module('weather')
@perms.require_all(
	'edit', 'admin',
	perform_on_self=(False, True),
	data_func=lambda **kwargs: kwargs.get('userdata', {})
)
@handle_client_exceptions
def resolve_update_weather_user(_, _info: GraphQLResolveInfo, userdata: dict) -> dict:
	return {'__typename': 'WeatherUser', **update_user(userdata)}


@mutation.field('logWeatherAlert')
@perms.module('weather')
@perms.require('notify')
def resolve_log_weather_alert(_, _info: GraphQLResolveInfo, users: list[str], error: str | None) -> dict:
	log_weather_alert(users, error)
	return {'__typename': 'LogResult', 'result': True}


@mutation.field('logUserWeatherAlert')
@perms.module('weather')
@perms.require('notify')
def resolve_log_user_weather_alert(_, _info: GraphQLResolveInfo, username: str, message: str) -> dict:
	log_user_weather_alert(username, message)
	return {'__typename': 'LogResult', 'result': True}
