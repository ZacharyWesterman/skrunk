from application.db.settings import set_module_enabled, get_enabled_modules, set_config, create_theme, delete_theme
import application.db.perms as perms
from ..decorators import *

@perms.require('admin')
def resolve_set_module_enabled(_, info, module_id: str, enabled: bool, group: str|None) -> list:
	set_module_enabled(module_id, enabled, group)
	return get_enabled_modules()

@perms.require('admin')
def resolve_set_config_value(_, info, name: str, value: str|None) -> bool:
	set_config(name, value)
	return True

@perms.require('admin')
@handle_client_exceptions
def resolve_create_theme(_, info, theme: dict) -> dict:
	return { '__typename': 'Theme', **create_theme(theme) }

@perms.require('admin')
@handle_client_exceptions
def resolve_delete_theme(_, info, name: str) -> dict:
	return { '__typename': 'Theme', **delete_theme(name)}
