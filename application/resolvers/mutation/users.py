"""application.resolvers.mutation.users"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.users import (create_reset_code, create_user, delete_user,
                                  export_user_data, unlock_user,
                                  update_user_disabled,
                                  update_user_display_name, update_user_email,
                                  update_user_groups, update_user_module,
                                  update_user_password, update_user_perms,
                                  update_user_theme, update_username)

from ..decorators import handle_client_exceptions
from . import mutation


@mutation.field('createUser')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_create_user(
	_,
	_info: GraphQLResolveInfo,
	username: str,
	password: str,
	groups: list
) -> dict:
	"""
	Creates a new user with the specified username, password, and groups.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username for the new user.
		password (str): The password for the new user.
		groups (list): List of groups to assign to the new user.

	Returns:
		dict: A dictionary containing the created user's data.
	"""
	return {'__typename': 'UserData', **create_user(username, password, groups=groups)}


@mutation.field('deleteUser')
@perms.require('admin')
@handle_client_exceptions
def resolve_delete_user(_, _info: GraphQLResolveInfo, username: str) -> dict:
	"""
	Deletes a user by username and returns the result as a dictionary.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user to delete.

	Returns:
		dict: A dictionary containing the deleted user data.
	"""
	return {'__typename': 'UserData', **delete_user(username)}


@perms.module('theme')
@mutation.field('updateUserTheme')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_user_theme(_, _info: GraphQLResolveInfo, username: str, theme: dict) -> dict:
	"""
	Updates the theme settings for a user and returns the updated user data.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user whose theme is to be updated.
		theme (dict): A dictionary containing the new theme settings for the user.

	Returns:
		dict: A dictionary representing the updated user data.
	"""
	return {'__typename': 'UserData', **update_user_theme(username, theme)}


@perms.module('theme')
@mutation.field('deleteUserTheme')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_delete_user_theme(_, _info: GraphQLResolveInfo, username: str) -> dict:
	"""
	Deletes the theme settings for a user by resetting their 'colors' and 'sizes' preferences.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user whose theme settings are to be deleted.

	Returns:
		dict: A dictionary containing the updated user data.
	"""
	return {'__typename': 'UserData', **update_user_theme(username, {'colors': [], 'sizes': []})}


# pylint: disable=redefined-outer-name
@mutation.field('updateUserPerms')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_user_perms(_, _info: GraphQLResolveInfo, username: str, perms: list) -> dict:
	"""
	Updates the permissions for a specified user.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user whose permissions are to be updated.
		perms (list): A list of permissions to assign to the user.

	Returns:
		dict: A dictionary containing the updated user data.
	"""
	return {'__typename': 'UserData', **update_user_perms(username, perms)}
# pylint: enable=redefined-outer-name


@mutation.field('updateUserPassword')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_user_password(
	_,
	_info: GraphQLResolveInfo,
	username: str,
	password: str
) -> dict:
	"""
	Updates the password for a specified user.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user whose password is to be updated.
		password (str): The new password to set for the user.

	Returns:
		dict: A dictionary containing the updated user data.
	"""
	return {'__typename': 'UserData', **update_user_password(username, password)}


@mutation.field('updateUsername')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_username(_, _info: GraphQLResolveInfo, username: str, newvalue: str) -> dict:
	"""
	Updates the username for a user and returns the updated user data.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The current username of the user to update.
		newvalue (str): The new username value to set.

	Returns:
		dict: A dictionary containing the updated user data.
	"""
	return {'__typename': 'UserData', **update_username(username, newvalue)}


@mutation.field('updateUserDisplayName')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_user_display_name(
	_,
	_info: GraphQLResolveInfo,
	username: str,
	display_name: str
) -> dict:
	"""
	Updates the display name of a user and returns the updated user data.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user whose display name is to be updated.
		display_name (str): The new display name for the user.

	Returns:
		dict: A dictionary containing the updated user data.
	"""
	return {'__typename': 'UserData', **update_user_display_name(username, display_name)}


@mutation.field('updateUserGroups')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_set_user_groups(_, _info: GraphQLResolveInfo, username: str, groups: list) -> dict:
	"""
	Updates the groups associated with a specified user and returns the updated user data.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user whose groups are to be updated.
		groups (list): A list of groups to assign to the user.

	Returns:
		dict: A dictionary containing the updated user data.
	"""
	return {'__typename': 'UserData', **update_user_groups(username, groups)}


@mutation.field('updateUserModule')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_set_user_module(_, _info: GraphQLResolveInfo, username: str, module: str, disabled: bool) -> dict:
	"""
	Updates the module status for a given user and returns the updated user data.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user whose module status is to be updated.
		module (str): The name of the module to update.
		disabled (bool): Flag indicating whether the module should be disabled.

	Returns:
		dict: A dictionary containing the updated user data.
	"""
	return {'__typename': 'UserData', **update_user_module(username, module, disabled)}


@mutation.field('updateUserEmail')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_update_user_email(_, _info: GraphQLResolveInfo, username: str, email: str) -> dict:
	"""
	Updates the email address of a user and returns the updated user data.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user whose email is to be updated.
		email (str): The new email address to set for the user.

	Returns:
		dict: A dictionary containing the updated user data.
	"""
	return {'__typename': 'UserData', **update_user_email(username, email)}


@mutation.field('exportUserData')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_export_user_data(_, _info: GraphQLResolveInfo, username: str) -> dict:
	"""
	Exports user data for the specified username.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user whose data is to be exported.

	Returns:
		dict: A dictionary representing the blob containing the exported user data.
	"""
	return {'__typename': 'Blob', **export_user_data(username)}


@mutation.field('unlockUser')
@perms.require('admin')
@handle_client_exceptions
def resolve_unlock_user(_, _info: GraphQLResolveInfo, username: str) -> dict:
	"""
	Unlocks a user account by username and returns user data.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user to unlock.

	Returns:
		dict: A dictionary containing the unlocked user's data.
	"""
	return {'__typename': 'UserData', **unlock_user(username)}


@mutation.field('adminCreateResetCode')
@perms.require('admin')
@handle_client_exceptions
def resolve_admin_create_reset_code(_, _info: GraphQLResolveInfo, username: str) -> dict:
	"""
	Requests a password reset code for the specified user.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user to request a reset code for.

	Returns:
		dict: A dictionary indicating success or failure of the request.
	"""

	# Delete any existing codes for this user, so rate limiting doesn't kick in
	# if an admin is trying to help them.

	code = create_reset_code(username, delete_existing=True)
	return {
		'__typename': 'ResetCode',
		'code': code,
	}


@mutation.field('updateUserDisabled')
@perms.require('admin')
@handle_client_exceptions
def resolve_update_user_disabled(
	_,
	_info: GraphQLResolveInfo,
	username: str,
	disabled: bool
) -> dict:
	"""
	Updates whether the user is disabled or not. If disabled,
	then the user cannot login or navigate around the site.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user.
		disabled (bool): Whether the user is disabled.

	Returns:
		dict: The updated user data.
	"""

	return {'__typename': 'UserData', **update_user_disabled(username, disabled)}
