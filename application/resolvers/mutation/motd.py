"""application.resolvers.mutation.motd"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.motd import create_motd, delete_motd
from application.types import Motd

from ..decorators import handle_client_exceptions, typed
from . import mutation


@mutation.field('createMotd')
@perms.require('admin')
@handle_client_exceptions
@typed
def resolve_create_motd(_, _info: GraphQLResolveInfo, text: str) -> Motd:
	"""
	Resolver to create a Messge of the Day with the given text.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		text (str): The text of the new MOTD.

	Returns:
		Motd: The created MOTD.
	"""
	return create_motd(text)


@mutation.field('deleteMotd')
@perms.require('admin')
@handle_client_exceptions
@typed
def resolve_delete_motd(_, _info: GraphQLResolveInfo, id: str) -> Motd:
	"""
	Resolver to delete a Message of the Day with the given ID.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The ID of the MOTD.

	Returns:
		Motd: The deleted MOTD if deletion was successful.
	"""
	return delete_motd(id)
