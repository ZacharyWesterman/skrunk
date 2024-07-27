from application.db.users import *
import application.db.perms as perms
from ..decorators import *

@perms.require(['admin'], perform_on_self = True)
@handle_client_exceptions
def resolve_create_user(_, info, username: str, password: str, groups: list) -> dict:
	userdata = create_user(username, password, groups = groups)
	return { '__typename' : 'UserData', **userdata }

@perms.require(['admin'])
@handle_client_exceptions
def resolve_delete_user(_, info, username: str) -> dict:
	userdata = delete_user(username)
	return { '__typename' : 'UserData', **userdata }

@perms.module('theme')
@perms.require(['admin'], perform_on_self = True)
@handle_client_exceptions
def resolve_update_user_theme(_, info, username: str, theme: dict) -> dict:
	userdata = update_user_theme(username, theme)
	return { '__typename': 'UserData', **userdata }

@perms.module('theme')
@perms.require(['admin'], perform_on_self = True)
@handle_client_exceptions
def resolve_delete_user_theme(_, info, username: str) -> dict:
	userdata = update_user_theme(username, {'colors': [], 'sizes': []})
	return { '__typename': 'UserData', **userdata }

@perms.require(['admin'], perform_on_self = True)
@handle_client_exceptions
def resolve_update_user_perms(_, info, username: str, perms: list) -> dict:
	userdata = update_user_perms(username, perms)
	return { '__typename': 'UserData', **userdata }

@perms.require(['admin'], perform_on_self = True)
@handle_client_exceptions
def resolve_update_user_password(_, info, username: str, password: str) -> dict:
	userdata = update_user_password(username, password)
	return { '__typename': 'UserData', **userdata }

@perms.require(['admin'], perform_on_self = True)
@handle_client_exceptions
def resolve_update_user_display_name(_, info, username: str, display_name: str) -> dict:
	userdata = update_user_display_name(username, display_name)
	return { '__typename': 'UserData', **userdata }

@perms.require(['admin'], perform_on_self = True)
@handle_client_exceptions
def resolve_set_user_groups(_, info, username: str, groups: list) -> dict:
	return { '__typename': 'UserData', **update_user_groups(username, groups) }

@perms.require(['admin'], perform_on_self = True)
@handle_client_exceptions
def resolve_set_user_module(_, info, username: str, module: str, disabled: bool) -> dict:
	return { '__typename': 'UserData', **update_user_module(username, module, disabled) }

@perms.require(['admin'], perform_on_self = True)
@handle_client_exceptions
def resolve_update_user_email(_, info, username: str, email: str) -> dict:
	return { '__typename': 'UserData', **update_user_email(username, email) }
