"""Resolvers for mutating Documents."""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.documents import (create_document, delete_document,
                                      get_document, update_document)

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
