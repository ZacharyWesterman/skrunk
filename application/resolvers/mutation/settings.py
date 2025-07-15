"""application.resolvers.mutation.settings"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.settings import (create_theme, delete_theme,
                                     get_enabled_modules, set_config,
                                     set_module_enabled)

from ..decorators import handle_client_exceptions
from . import mutation


@mutation.field('setModuleEnabled')
@perms.require('admin')
def resolve_set_module_enabled(_, _info: GraphQLResolveInfo, module_id: str, enabled: bool, group: str | None) -> list:
	"""
	Enables or disables a module for a specified group and returns the updated list of enabled modules.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		module_id (str): The unique identifier of the module to enable or disable.
		enabled (bool): Flag indicating whether the module should be enabled (True) or disabled (False).
		group (str | None): The group for which the module's enabled state should be set.
			If None, applies globally to all groups.

	Returns:
		list: The updated list of enabled modules after the change.
	"""
	set_module_enabled(module_id, enabled, group)
	return get_enabled_modules()


@mutation.field('setConfig')
@perms.require('admin')
def resolve_set_config_value(_, _info: GraphQLResolveInfo, name: str, value: str | None) -> bool:
	"""
	Sets a configuration value by name.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		name (str): The name of the configuration setting to update.
		value (str | None): The value to set for the configuration setting.
			If None, the setting is erased.

	Returns:
		bool: True if the configuration value was set successfully.
	"""
	set_config(name, value)
	return True


@mutation.field('createTheme')
@perms.require('admin')
@handle_client_exceptions
def resolve_create_theme(_, _info: GraphQLResolveInfo, theme: dict) -> dict:
	"""
	Resolves the creation of a new theme.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		theme (dict): A dictionary containing the theme data to be created.

	Returns:
		dict: A dictionary representing the newly created theme.
	"""
	return {'__typename': 'Theme', **create_theme(theme)}


@mutation.field('deleteTheme')
@perms.require('admin')
@handle_client_exceptions
def resolve_delete_theme(_, _info: GraphQLResolveInfo, name: str) -> dict:
	"""
	Deletes a theme by its name and returns a dictionary representing the deleted theme.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		name (str): The name of the theme to delete.

	Returns:
		dict: A dictionary representing the deleted theme.
	"""
	return {'__typename': 'Theme', **delete_theme(name)}
