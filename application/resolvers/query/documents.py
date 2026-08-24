"""Resolvers for querying Documents."""

from graphql.type import GraphQLResolveInfo
from tag_query import exceptions

from application.db import perms
from application.db.documents import (count_documents, count_tag_uses,
                                      get_document, get_documents,
                                      sum_document_size)
from application.types import DocumentSearchFilter

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
@handle_client_exceptions
def resolve_get_documents(
	_,
	_info: GraphQLResolveInfo,
	filter: DocumentSearchFilter,
	start: int,
	count: int
) -> dict:
	"""
	Resolves the retrieval of documents based on pagination.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		filter (DocumentSearchFilter): A TypedDict containing filtering options.
		start (int): The starting index for pagination.
		count (int): The number of books to retrieve.

	Returns:
		dict: A list of documents.
	"""

	try:
		return {'__typename': 'DocumentList', 'documents': get_documents(filter, start, count)}
	except exceptions.ParseError as e:
		return {'__typename': 'BadTagQuery', 'message': str(e)}


@query.field('countDocuments')
@perms.module('documents')
@handle_client_exceptions
def resolve_count_documents(_, _info: GraphQLResolveInfo, filter: DocumentSearchFilter) -> dict:
	"""
	Resolves the retrieval of the total number of documents.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		filter (DocumentSearchFilter): A TypedDict containing filtering options.

	Returns:
		dict: A dictionary containing just the document count.
	"""
	try:
		return {'__typename': 'DocumentCount', 'count': count_documents(filter)}
	except exceptions.ParseError as e:
		return {'__typename': 'BadTagQuery', 'message': str(e)}


@query.field('countDocumentTagUses')
@perms.module('documents')
def resolve_count_tag_uses(_, _info: GraphQLResolveInfo, tag: str) -> int:
	"""
	Resolves the number of times a specific tag has been used in documents available to the caller.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		tag (str): The tag to count usages for.

	Returns:
		int: The number of times the specified tag has been used.
	"""
	return count_tag_uses(tag)


@query.field('totalDocumentSize')
@perms.module('documents')
def resolve_total_document_size(_, _info: GraphQLResolveInfo, filter: DocumentSearchFilter) -> dict:
	"""
	Resolves the total size of documents matching the given filter.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		filter (DocumentSearchFilter): Filter criteria for searching documents.

	Returns:
		dict: A dictionary representing the total size of all documents matching the filter,
			or a BadTagQuery if a ParseError occurs.
	"""
	try:
		return {'__typename': 'BlobCount', 'count': sum_document_size(filter)}
	except exceptions.ParseError as e:
		return {'__typename': 'BadTagQuery', 'message': str(e)}
