"""application.resolvers.query.settings"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.settings import (get_all_configs, get_all_themes,
                                     get_config, get_enabled_modules,
                                     get_groups, get_modules)
from application.integrations import graphql

from . import query


@query.field('getEnabledModules')
def resolve_get_enabled_modules(_, _info: GraphQLResolveInfo) -> list:
	"""
	Resolves and returns a list of enabled modules for the current caller.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		list: A list of enabled modules accessible to the caller based on strict permissions.
	"""
	return get_enabled_modules(perms.caller_info_strict())


@query.field('getModules')
def resolve_get_modules(_, _info: GraphQLResolveInfo) -> list:
	"""
	Resolves and returns a list of modules accessible to the caller.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		list: A list of modules available to the caller based on permission checks.
	"""
	return get_modules(perms.caller_info_strict())


@query.field('getServerEnabledModules')
def resolve_get_server_enabled_modules(_, _info: GraphQLResolveInfo, group: str | None) -> list:
	"""
	Retrieves the list of enabled server modules for a specified group.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		group (str | None): The group identifier to filter enabled modules, or None for all groups.

	Returns:
		list: A list of enabled module names for the specified group.
	"""
	return get_enabled_modules(group=group)


@query.field('getUserGroups')
def resolve_get_groups(_, _info: GraphQLResolveInfo) -> list:
	"""
	Resolves the GraphQL query for retrieving a list of groups.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		list: A list of all user groups.
	"""
	return get_groups()


@query.field('getConfigs')
@perms.require('admin')
def resolve_get_all_configs(_, _info: GraphQLResolveInfo) -> dict:
	"""
	Resolves the GraphQL query for retrieving all configuration objects.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		dict: A dictionary containing a list of all configuration objects.
	"""
	return {'__typename': 'ConfigList', 'configs': get_all_configs()}


@query.field('getConfig')
def resolve_get_config(_, _info: GraphQLResolveInfo, name: str) -> str | None:
	"""
	Retrieves the configuration value for the given name.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		name (str): The name of the configuration setting to retrieve.

	Returns:
		str | None: The configuration value if found, otherwise None.
	"""
	return get_config(name)


@query.field('getThemes')
@perms.module('theme')
def resolve_get_themes(_, _info: GraphQLResolveInfo) -> list:
	"""
	Resolves the GraphQL query for retrieving all available themes.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		list: A list of all available themes.
	"""
	return get_all_themes()


@query.field('getSchema')
def resolve_get_schema(_, _info: GraphQLResolveInfo) -> dict:
	"""
	Resolves and returns the current GraphQL schema as a dictionary.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		dict: The current GraphQL schema.
	"""
	return graphql.schema()
