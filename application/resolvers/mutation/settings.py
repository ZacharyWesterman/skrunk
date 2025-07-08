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
	set_module_enabled(module_id, enabled, group)
	return get_enabled_modules()


@mutation.field('setConfig')
@perms.require('admin')
def resolve_set_config_value(_, _info: GraphQLResolveInfo, name: str, value: str | None) -> bool:
	set_config(name, value)
	return True


@mutation.field('createTheme')
@perms.require('admin')
@handle_client_exceptions
def resolve_create_theme(_, _info: GraphQLResolveInfo, theme: dict) -> dict:
	return {'__typename': 'Theme', **create_theme(theme)}


@mutation.field('deleteTheme')
@perms.require('admin')
@handle_client_exceptions
def resolve_delete_theme(_, _info: GraphQLResolveInfo, name: str) -> dict:
	return {'__typename': 'Theme', **delete_theme(name)}
