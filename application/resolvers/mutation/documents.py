"""Resolvers for mutating Documents."""

from graphql.type import GraphQLResolveInfo
from tag_query import exceptions

from application.db import perms
from application.db.documents import (create_document, delete_document,
                                      get_document, link_document,
                                      set_document_tags, update_document,
                                      zip_matching_documents)
from application.types import DocumentSearchFilter

from ..decorators import handle_client_exceptions
from . import mutation


@mutation.field('createDocument')
@perms.module('documents')
@perms.require('edit')
@handle_client_exceptions
def resolve_create_document(
	_,
    _info: GraphQLResolveInfo,
    title: str,
    body: str
) -> dict:
	"""
	Resolver function to create a new document.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		title (str): The title of the document.
		body (str): The body content of the document.

	Returns:
		dict: A dictionary representing the created document with a '__typename' key.
	"""
	return {'__typename': 'Document', **create_document(title, body, False)}


@mutation.field('createBlobDocument')
@perms.module('documents')
@perms.require('edit')
@handle_client_exceptions
def resolve_create_blob_document(
	_,
	_info: GraphQLResolveInfo,
	title: str
) -> dict:
	"""
	Resolver function to create a new blob document.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		title (str): The title of the document.

	Returns:
		dict: A dictionary representing the created document with a '__typename' key.
	"""
	return {'__typename': 'Document', **create_document(title, '', True)}


@mutation.field('linkBlobDocument')
@perms.module('documents')
@perms.require('edit')
@handle_client_exceptions
def resolve_link_blob_document(
	_,
	_info: GraphQLResolveInfo,
	title: str,
	blob_id: str,
) -> dict:
	"""
	Resolver function to create a new blob document and link it to an existing blob.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		title (str): The title of the document.

	Returns:
		dict: A dictionary representing the created document with a '__typename' key.
	"""
	return {'__typename': 'Document', **link_document(title, blob_id)}


@mutation.field('updateDocument')
@perms.module('documents')
@perms.require('edit')
@perms.require('admin', perform_on_self=True, data_func=get_document)
@handle_client_exceptions
def resolve_update_document(
	_,
	_info: GraphQLResolveInfo,
    id: str,
    title: str | None,
    body: str | None
) -> dict:
	"""
	Resolver function to update a document.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the document to be updated.
		title (str | None): The new title of the document. If None, the title will not be updated.
		body (str | None): The new body content of the document. If None, the body will not be updated.

	Returns:
		dict: A dictionary representing the updated document with a '__typename' key.
	"""
	return {'__typename': 'Document', **update_document(id, title, body)}


@mutation.field('setDocumentTags')
@perms.module('documents')
@perms.require('edit')
@handle_client_exceptions
def resolve_set_document_tags(_, _info: GraphQLResolveInfo, id: str, tags: list[str]) -> dict:
	"""
	Resolves the mutation for setting tags on a document object.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the document to update.
		tags (list[str]): A list of tags to assign to the document.

	Returns:
		dict: A dictionary representing the updated document.
	"""
	return {'__typename': 'Document', **set_document_tags(id, tags)}


@mutation.field('deleteDocument')
@perms.module('documents')
@perms.require('edit')
@perms.require('admin', perform_on_self=True, data_func=get_document)
@handle_client_exceptions
def resolve_delete_document(_, _info: GraphQLResolveInfo, id: str) -> dict:
	"""
	Resolver function to delete a document.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the document to be deleted.

	Returns:
		dict: A dictionary containing the typename and the document that was deleted.
	"""
	return {'__typename': 'Document', **delete_document(id)}


@mutation.field('createDocumentZipArchive')
@perms.module('documents', 'files')
@perms.require('edit')
@handle_client_exceptions
def resolve_create_document_zip_archive(_, _info: GraphQLResolveInfo, filter: DocumentSearchFilter, uid: str) -> dict:
	try:
		blob = zip_matching_documents(filter, uid)
		return {'__typename': 'Blob', **blob}
	except exceptions.ParseError as e:
		return {'__typename': 'BadTagQuery', 'message': str(e)}
