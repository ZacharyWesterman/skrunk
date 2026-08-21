"""Resolvers for querying Documents."""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.documents import (count_documents, get_document,
                                      get_documents)

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


@query.field('getDocuments')
@perms.module('documents')
def resolve_get_documents(_, _info: GraphQLResolveInfo, start: int, count: int) -> list[dict]:
	"""
	Resolves the retrieval of documents based on pagination.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		start (int): The starting index for pagination.
		count (int): The number of books to retrieve.

	Returns:
		list[dict]: A list of documents.
	"""
	return get_documents(start, count)


@query.field('countDocuments')
@perms.module('documents')
def resolve_count_documents(_, _info: GraphQLResolveInfo) -> dict:
	return {'__typename': 'DocumentCount', 'count': count_documents()}
