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

	# Require one of the following to be true:
	# - The document is owned by this user
	# - The document was explicitly shared with this user
	# - The document was shared with one of this user's groups

	doc = get_document(id)
	user_data = perms.caller_info_strict()

	if (
		doc['creator'].get('_id') != user_data.get('_id') and
		user_data.get('_id') not in doc['shared_users'] and
		not any(group in doc['shared_groups'] for group in user_data['groups'])
	):
		return perms.bad_perms()

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
	"""
	Resolves the retrieval of the total number of documents.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		dict: A dictionary containing just the document count.
	"""
	return {'__typename': 'DocumentCount', 'count': count_documents()}
