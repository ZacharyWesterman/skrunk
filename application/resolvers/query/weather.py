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
	"""
	Resolves the GraphQL query for retrieving weather information for a specific user.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username for which to fetch weather data.

	Returns:
		dict: A dictionary containing weather information for the user.
	"""
	return {'__typename': 'WeatherUser', **process_weather_user(get_weather_user(username))}


@query.field('getWeatherUsers')
@perms.module('weather')
def resolve_get_weather_users(_, _info: GraphQLResolveInfo) -> list:
	"""
	Resolves the query to retrieve weather users.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		list: A list of users who have access to weather data.
	"""
	return get_users()


@query.field('getLastWeatherExec')
@perms.module('weather')
def resolve_get_last_execution(_, _info: GraphQLResolveInfo) -> dict | None:
	"""
	Retrieves the result of the most recent weather alerts execution.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		dict | None: The execution result as a dictionary, or None if no execution has occurred.
	"""
	return get_last_exec()


@query.field('weatherAlertHistory')
@perms.module('weather')
def resolve_get_alert_history(_, _info: GraphQLResolveInfo, start: int, count: int) -> list:
	"""
	Retrieves a list of alert history records starting from a specified index.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		start (int): The starting index for retrieving alert history.
		count (int): The number of alert history records to retrieve.

	Returns:
		list: A list containing the alert history records.
	"""
	return get_alert_history(None, start, count)


@query.field('getWeatherAlerts')
@perms.module('weather')
@perms.require('admin', perform_on_self=True)
def resolve_get_weather_alerts(_, _info: GraphQLResolveInfo, username: str, start: int, count: int) -> list:
	"""
	Fetches a list of weather alerts for a given user within a specified range.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username for which to retrieve weather alerts.
		start (int): The starting index for alert history retrieval.
		count (int): The number of alerts to retrieve.

	Returns:
		list: A list of weather alert objects for the specified user and range.
	"""
	return get_alert_history(username, start, count)


@query.field('countWeatherAlerts')
@perms.module('weather')
@perms.require('admin', perform_on_self=True)
def resolve_count_weather_alerts(_, _info: GraphQLResolveInfo, username: str) -> int:
	"""
	Resolves the count of weather alerts for a given user.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username for which to count weather alerts.

	Returns:
		int: The number of weather alerts associated with the specified user.
	"""
	return count_alert_history(username)
