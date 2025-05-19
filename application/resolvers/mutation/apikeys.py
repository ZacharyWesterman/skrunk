"""application.resolvers.mutation.apikeys"""

from graphql.type import GraphQLResolveInfo
from application.db.apikeys import new_api_key, delete_api_key
from application.db import perms
from . import mutation


@mutation.field('createAPIKey')
@perms.require('admin')
def resolve_create_api_key(_, info: GraphQLResolveInfo, description: str, permissions: list[str]) -> str:
	"""
	Resolver function to create a new API key.

	Args:
		_ (Any): Placeholder.
		info (GraphQLResolveInfo): Information about the GraphQL execution state.
		description (str): A description for the new API key.
		permissions (list[str]): A list of permissions to be associated with the new API key.

	Returns:
		str: The newly created API key.
	"""
	return new_api_key(description, permissions)


@mutation.field('deleteAPIKey')
@perms.require('admin')
def resolve_delete_api_key(_, info: GraphQLResolveInfo, key: str) -> bool:
	"""
	Resolver function to delete an API key.

	Args:
		_ (Any): Placeholder.
		info (GraphQLResolveInfo): Information about the GraphQL execution state.
		key (str): The API key to be deleted.

	Returns:
		bool: True if the API key was successfully deleted, False otherwise.
	"""
	return delete_api_key(key)
