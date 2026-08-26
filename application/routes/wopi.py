"""application.routes.wopi"""
from flask import Response, jsonify, request

from application.db import users
from application.db.blob import get_blob_data
from application.db.documents import get_document, update_document
from application.exceptions import (BlobDoesNotExistError,
                                    DocumentDoesNotExistError)
from application.tokens import decode_user_token, token_is_valid
from application.types.blob_storage import BlobStorage


def get_document_contents(jwt: str, id: str) -> Response:
	"""
	Get the contents of a document via WOPI endpoint.

	Args:
		jwt (str): A valid JSON web token string.
		id (str): The ID of the document.

	Returns:
		Response: A response containing either the body of the document or an error, as appropriate.
	"""

	if not token_is_valid(jwt):
		return Response('Access denied.', 403)

	try:
		doc = get_document(id)
	except DocumentDoesNotExistError:
		return Response('File not found.', 404)

	user_data = users.get_user_data(decode_user_token(jwt).get('username', ''))

	if (
		doc['creator'].get('_id') != user_data.get('_id') and
		user_data.get('_id') not in doc['shared_users'] and
		not any(group in doc['shared_groups'] for group in user_data['groups'])
	):
		return Response('Access denied.', 403)

	if doc['blob_id'] is None:
		return doc['body']

	try:
		blob = get_blob_data(doc['blob_id'])
	except BlobDoesNotExistError:
		return Response('Blob data not found.', 404)

	with open(BlobStorage(doc['blob_id'], blob['ext']).path(), 'rb') as fp:
		return Response(fp.read())


def put_document_contents(jwt: str, id: str) -> Response:
	"""
	Update the contents of a document via WOPI endpoint.

	Args:
		jwt (str): A valid JSON web token string.
		id (str): The ID of the document.

	Returns:
		Response: A response containing 'OK' on success, or an error as appropriate.
	"""

	if not token_is_valid(jwt):
		return Response('Access denied.', 403)

	try:
		doc = get_document(id)
	except DocumentDoesNotExistError:
		return Response('File not found', 404)

	user_data: dict = users.get_user_data(decode_user_token(jwt).get('username', ''))  # type: ignore

	if (
		doc['creator'].get('_id') != user_data.get('_id') and
		user_data.get('_id') not in doc['shared_users'] and
		not any(group in doc['shared_groups'] for group in user_data['groups'])
	):
		return Response('Access denied.', 403)

	try:
		update_document(id, None, request.data, user_data=user_data)
	except DocumentDoesNotExistError:
		return Response('File not found', 404)

	return Response('OK')


def get_document_info(jwt: str, id: str) -> Response:
	"""
	Get info about a document via WOPI endpoint.

	```json
	{
		"BaseFileName": (str) the title of the document,
		"Size": (int) the document size in bytes,
		"UserCanWrite": (bool) true if the user owns this document, false otherwise
	}
	```

	Args:
		jwt (str): A valid JSON web token string.
		id (str): The ID of the document.

	Returns:
		Response: A response containing either JSON info about the document, or an error as appropriate.
	"""

	if not token_is_valid(jwt):
		return Response('Access denied.', 403)

	try:
		doc = get_document(id)
	except DocumentDoesNotExistError:
		return Response('File not found', 404)

	user_data: dict = users.get_user_data(decode_user_token(jwt).get('username', ''))  # type: ignore

	doc_size = len(doc['body'])
	if doc['blob_id'] is not None:
		try:
			blob_data = get_blob_data(doc['blob_id'])
			doc_size = blob_data['size']
		except BlobDoesNotExistError:
			pass

	username = user_data['username']
	display_name: str = user_data.get('display_name', '')
	if display_name == '':
		display_name = username
	if display_name.lower() != username:
		display_name += f' ({username})'

	last_modified = doc['updated']
	if last_modified is None:
		last_modified = doc['created']

	return jsonify({
		'BaseFileName': doc.get('title', 'Untitled Document'),
		'Size': doc_size,
		'OwnerId': str(doc['creator']),
		'UserId': str(user_data.get('_id')),
		'UserFriendlyName': display_name,
		'UserCanWrite': user_data['_id'] == doc['creator'].get('_id'),
		'LastModifiedTime': last_modified,
	})
