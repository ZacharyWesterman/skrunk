"""application.resolvers.mutation.users"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.users import (create_user, delete_user, export_user_data,
                                  update_user_display_name, update_user_email,
                                  update_user_groups, update_user_module,
                                  update_user_password, update_user_perms,
                                  update_user_theme, update_username)

from ..decorators import handle_client_exceptions
from . import mutation


@mutation.field('createUser')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_create_user(_, _info: GraphQLResolveInfo, username: str, password: str, groups: list) -> dict:
	return {'__typename': 'UserData', **create_user(username, password, groups=groups)}


@mutation.field('deleteUser')
@perms.require('admin')
@handle_client_exceptions
def resolve_delete_user(_, _info: GraphQLResolveInfo, username: str) -> dict:
	return {'__typename': 'UserData', **delete_user(username)}


@perms.module('theme')
@mutation.field('updateUserTheme')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_user_theme(_, _info: GraphQLResolveInfo, username: str, theme: dict) -> dict:
	return {'__typename': 'UserData', **update_user_theme(username, theme)}


@perms.module('theme')
@mutation.field('deleteUserTheme')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_delete_user_theme(_, _info: GraphQLResolveInfo, username: str) -> dict:
	return {'__typename': 'UserData', **update_user_theme(username, {'colors': [], 'sizes': []})}


# pylint: disable=redefined-outer-name
@mutation.field('updateUserPerms')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_user_perms(_, _info: GraphQLResolveInfo, username: str, perms: list) -> dict:
	return {'__typename': 'UserData', **update_user_perms(username, perms)}
# pylint: enable=redefined-outer-name


@mutation.field('updateUserPassword')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_user_password(_, _info: GraphQLResolveInfo, username: str, password: str) -> dict:
	return {'__typename': 'UserData', **update_user_password(username, password)}


@mutation.field('updateUsername')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_username(_, _info: GraphQLResolveInfo, username: str, newvalue: str) -> dict:
	return {'__typename': 'UserData', **update_username(username, newvalue)}


@mutation.field('updateUserDisplayName')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_user_display_name(_, _info: GraphQLResolveInfo, username: str, display_name: str) -> dict:
	return {'__typename': 'UserData', **update_user_display_name(username, display_name)}


@mutation.field('updateUserGroups')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_set_user_groups(_, _info: GraphQLResolveInfo, username: str, groups: list) -> dict:
	return {'__typename': 'UserData', **update_user_groups(username, groups)}


@mutation.field('updateUserModule')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_set_user_module(_, _info: GraphQLResolveInfo, username: str, module: str, disabled: bool) -> dict:
	return {'__typename': 'UserData', **update_user_module(username, module, disabled)}


@mutation.field('updateUserEmail')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_user_email(_, _info: GraphQLResolveInfo, username: str, email: str) -> dict:
	return {'__typename': 'UserData', **update_user_email(username, email)}


@mutation.field('exportUserData')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_export_user_data(_, _info: GraphQLResolveInfo, username: str) -> dict:
	return {'__typename': 'Blob', **export_user_data(username)}
