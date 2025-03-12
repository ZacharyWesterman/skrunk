"""application.resolvers.mutation.settings"""

from ariadne.types import GraphQLResolveInfo
from application.db.settings import set_module_enabled, get_enabled_modules, set_config, create_theme, delete_theme
import application.db.perms as perms
from ..decorators import *
from . import mutation


@mutation.field('setModuleEnabled')
@perms.require('admin')
def resolve_set_module_enabled(_, info: GraphQLResolveInfo, module_id: str, enabled: bool, group: str | None) -> list:
	set_module_enabled(module_id, enabled, group)
	return get_enabled_modules()


@mutation.field('setConfig')
@perms.require('admin')
def resolve_set_config_value(_, info: GraphQLResolveInfo, name: str, value: str | None) -> bool:
	set_config(name, value)
	return True


@mutation.field('createTheme')
@perms.require('admin')
@handle_client_exceptions
def resolve_create_theme(_, info: GraphQLResolveInfo, theme: dict) -> dict:
	return {'__typename': 'Theme', **create_theme(theme)}


@mutation.field('deleteTheme')
@perms.require('admin')
@handle_client_exceptions
def resolve_delete_theme(_, info: GraphQLResolveInfo, name: str) -> dict:
	return {'__typename': 'Theme', **delete_theme(name)}
