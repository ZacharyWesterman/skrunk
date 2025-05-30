"""application.resolvers.query.users"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.users import get_user_data, get_user_list

from ..decorators import handle_client_exceptions
from . import query


@query.field('getUser')
@handle_client_exceptions
def resolve_get_user(_, _info: GraphQLResolveInfo, username: str) -> dict:
	return {'__typename': 'UserData', **get_user_data(username)}


@query.field('listUsers')
def resolve_list_users(_, _info: GraphQLResolveInfo, restrict: bool) -> list:
	user_data = perms.caller_info_strict()
	if not restrict and perms.user_has_perms(user_data, ('admin',)):
		return get_user_list([])
	return get_user_list(user_data.get('groups', []))
