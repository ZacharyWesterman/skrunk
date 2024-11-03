from application.db.users import *
import application.db.perms as perms
from ..decorators import *

@perms.require('admin', perform_on_self = True)
@handle_client_exceptions
def resolve_create_user(_, info, username: str, password: str, groups: list) -> dict:
	return { '__typename' : 'UserData', **create_user(username, password, groups = groups) }

@perms.require('admin')
@handle_client_exceptions
def resolve_delete_user(_, info, username: str) -> dict:
	return { '__typename' : 'UserData', **delete_user(username) }

@perms.module('theme')
@perms.require('admin', perform_on_self = True)
@handle_client_exceptions
def resolve_update_user_theme(_, info, username: str, theme: dict) -> dict:
	return { '__typename': 'UserData', **update_user_theme(username, theme) }

@perms.module('theme')
@perms.require('admin', perform_on_self = True)
@handle_client_exceptions
def resolve_delete_user_theme(_, info, username: str) -> dict:
	return { '__typename': 'UserData', **update_user_theme(username, {'colors': [], 'sizes': []}) }

@perms.require('admin', perform_on_self = True)
@handle_client_exceptions
def resolve_update_user_perms(_, info, username: str, perms: list) -> dict:
	return { '__typename': 'UserData', **update_user_perms(username, perms) }

@perms.require('admin', perform_on_self = True)
@handle_client_exceptions
def resolve_update_user_password(_, info, username: str, password: str) -> dict:
	return { '__typename': 'UserData', **update_user_password(username, password) }

@perms.require('admin', perform_on_self = True)
@handle_client_exceptions
def resolve_update_username(_, info, username: str, newvalue: str) -> dict:
	return { '__typename': 'UserData', **update_username(username, newvalue) }

@perms.require('admin', perform_on_self = True)
@handle_client_exceptions
def resolve_update_user_display_name(_, info, username: str, display_name: str) -> dict:
	return { '__typename': 'UserData', **update_user_display_name(username, display_name) }

@perms.require('admin', perform_on_self = True)
@handle_client_exceptions
def resolve_set_user_groups(_, info, username: str, groups: list) -> dict:
	return { '__typename': 'UserData', **update_user_groups(username, groups) }

@perms.require('admin', perform_on_self = True)
@handle_client_exceptions
def resolve_set_user_module(_, info, username: str, module: str, disabled: bool) -> dict:
	return { '__typename': 'UserData', **update_user_module(username, module, disabled) }

@perms.require('admin', perform_on_self = True)
@handle_client_exceptions
def resolve_update_user_email(_, info, username: str, email: str) -> dict:
	return { '__typename': 'UserData', **update_user_email(username, email) }

@perms.require('admin', perform_on_self = True)
@handle_client_exceptions
def resolve_export_user_data(_, info, username: str) -> dict:
	return { '__typename': 'Blob', **export_user_data(username) }
