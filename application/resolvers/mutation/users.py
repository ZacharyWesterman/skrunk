"""application.resolvers.mutation.users"""

from ariadne.types import GraphQLResolveInfo
from application.db.users import *
import application.db.perms as perms
from ..decorators import *
from . import mutation


@mutation.field('createUser')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_create_user(_, info: GraphQLResolveInfo, username: str, password: str, groups: list) -> dict:
	return {'__typename': 'UserData', **create_user(username, password, groups=groups)}


@mutation.field('deleteUser')
@perms.require('admin')
@handle_client_exceptions
def resolve_delete_user(_, info: GraphQLResolveInfo, username: str) -> dict:
	return {'__typename': 'UserData', **delete_user(username)}


@perms.module('theme')
@mutation.field('updateUserTheme')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_user_theme(_, info: GraphQLResolveInfo, username: str, theme: dict) -> dict:
	return {'__typename': 'UserData', **update_user_theme(username, theme)}


@perms.module('theme')
@mutation.field('deleteUserTheme')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_delete_user_theme(_, info: GraphQLResolveInfo, username: str) -> dict:
	return {'__typename': 'UserData', **update_user_theme(username, {'colors': [], 'sizes': []})}


@mutation.field('updateUserPerms')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_user_perms(_, info: GraphQLResolveInfo, username: str, perms: list) -> dict:
	return {'__typename': 'UserData', **update_user_perms(username, perms)}


@mutation.field('updateUserPassword')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_user_password(_, info: GraphQLResolveInfo, username: str, password: str) -> dict:
	return {'__typename': 'UserData', **update_user_password(username, password)}


@mutation.field('updateUsername')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_username(_, info: GraphQLResolveInfo, username: str, newvalue: str) -> dict:
	return {'__typename': 'UserData', **update_username(username, newvalue)}


@mutation.field('updateUserDisplayName')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_user_display_name(_, info: GraphQLResolveInfo, username: str, display_name: str) -> dict:
	return {'__typename': 'UserData', **update_user_display_name(username, display_name)}


@mutation.field('updateUserGroups')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_set_user_groups(_, info: GraphQLResolveInfo, username: str, groups: list) -> dict:
	return {'__typename': 'UserData', **update_user_groups(username, groups)}


@mutation.field('updateUserModule')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_set_user_module(_, info: GraphQLResolveInfo, username: str, module: str, disabled: bool) -> dict:
	return {'__typename': 'UserData', **update_user_module(username, module, disabled)}


@mutation.field('updateUserEmail')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_user_email(_, info: GraphQLResolveInfo, username: str, email: str) -> dict:
	return {'__typename': 'UserData', **update_user_email(username, email)}


@mutation.field('exportUserData')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_export_user_data(_, info: GraphQLResolveInfo, username: str) -> dict:
	return {'__typename': 'Blob', **export_user_data(username)}
