"""application.resolvers.query.users"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.users import get_user_data, get_user_list

from ..decorators import handle_client_exceptions
from . import query


@query.field('getUser')
@handle_client_exceptions
def resolve_get_user(_, _info: GraphQLResolveInfo, username: str) -> dict:
	"""
	Resolves the GraphQL query for retrieving user data by username.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user to retrieve data for.

	Returns:
		dict: A dictionary containing user data.
	"""
	return {'__typename': 'UserData', **get_user_data(username)}


@query.field('listUsers')
def resolve_list_users(_, _info: GraphQLResolveInfo, restrict: bool) -> list:
	"""
	Resolves and returns a list of users based on the caller's permissions and the restrict flag.

	Args:
		_ (Any): Unused positional argument, typically the parent resolver.
		_info (GraphQLResolveInfo): GraphQL resolver info containing context and query details.
		restrict (bool): If True, restricts the user list to the caller's groups.
			If False and caller is admin, returns all users.

	Returns:
		list: A list of users filtered by permissions and group membership.
	"""
	user_data = perms.caller_info_strict()
	if not restrict and perms.user_has_perms(user_data, ('admin',)):
		return get_user_list([])
	return get_user_list(user_data.get('groups', []))
