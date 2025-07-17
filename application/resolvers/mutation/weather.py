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
	"""
	Creates a new weather user and returns the user data.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		userdata (dict): Dictionary containing user data required for user creation.

	Returns:
		dict: A dictionary representing the created weather user.
	"""
	return {'__typename': 'WeatherUser', **create_user(userdata)}


@mutation.field('deleteWeatherUser')
@perms.module('weather')
@perms.require('admin')
@handle_client_exceptions
def resolve_delete_weather_user(_, _info: GraphQLResolveInfo, username: str) -> dict:
	"""
	Deletes a weather user by username.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the weather user to delete.

	Returns:
		dict: A dictionary representing the deleted weather user.
	"""
	return {'__typename': 'WeatherUser', **delete_user(username)}


@mutation.field('enableWeatherUser')
@perms.module('weather')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_enable_weather_user(_, _info: GraphQLResolveInfo, username: str) -> dict:
	"""
	Enables weather alerts for a specified user.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user to enable weather alerts for.

	Returns:
		dict: A dictionary representing the updated weather user.
	"""
	return {'__typename': 'WeatherUser', **set_user_excluded(username, False)}


@mutation.field('disableWeatherUser')
@perms.module('weather')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_disable_weather_user(_, _info: GraphQLResolveInfo, username: str) -> dict:
	"""
	Disables weather alerts for a specific user by setting their exclusion status.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user to disable weather alerts for.

	Returns:
		dict: A dictionary representing the updated weather user.
	"""
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
	"""
	Updates a weather user with the provided user data.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		userdata (dict): Dictionary containing user data to update.

	Returns:
		dict: A dictionary representing the updated weather user.
	"""
	return {'__typename': 'WeatherUser', **update_user(userdata)}


@mutation.field('logWeatherAlert')
@perms.module('weather')
@perms.require('notify')
def resolve_log_weather_alert(
	_,
    _info: GraphQLResolveInfo,
    users: list[str],
    error: str | None
) -> dict:
	"""
	Logs a weather alert for the specified users and returns the result.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		users (list[str]): List of user identifiers to log the weather alert for.
		error (str | None): Optional error message to log with the alert.

	Returns:
		dict: A dictionary representing the result of the logging operation.
	"""
	log_weather_alert(users, error)
	return {'__typename': 'LogResult', 'result': True}


@mutation.field('logUserWeatherAlert')
@perms.module('weather')
@perms.require('notify')
def resolve_log_user_weather_alert(
	_,
    _info: GraphQLResolveInfo,
    username: str,
    message: str
) -> dict:
	"""
	Logs a weather alert message for a specified user and returns the result.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user to log the weather alert for.
		message (str): The weather alert message to be logged.

	Returns:
		dict: A dictionary representing the result of the logging operation.
	"""
	log_user_weather_alert(username, message)
	return {'__typename': 'LogResult', 'result': True}
