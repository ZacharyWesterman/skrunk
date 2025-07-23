"""Resolvers for querying Documents."""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.documents import get_child_documents, get_document

from ..decorators import handle_client_exceptions
from . import query


@query.field('getDocument')
@perms.module('documents')
@handle_client_exceptions
def resolve_get_document(_, _info: GraphQLResolveInfo, id: str) -> dict:
	"""
	Resolver function to fetch a document by its ID.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The ID of the document to retrieve.

	Returns:
		dict: A dictionary representing the document with an added '__typename' key.
	"""
	return {'__typename': 'Document', **get_document(id)}


@query.field('getChildDocuments')
@perms.module('documents')
def resolve_get_child_documents(_, _info: GraphQLResolveInfo, id: str | None) -> list[dict]:
	"""
	Resolver function to get child documents for a given document ID.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str | None): The ID of the parent document for which to retrieve child documents.
			If None, retrieves top-level documents.

	Returns:
		list[dict]: A list of dictionaries representing the child documents.
	"""
	return get_child_documents(id)
