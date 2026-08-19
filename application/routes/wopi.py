
from flask import Response, jsonify, request

from application.db import users
from application.db.documents import (DocumentDoesNotExistError, get_document,
                                      update_document)
from application.tokens import decode_user_token, token_is_valid


def get_document_contents(jwt: str, id: str) -> Response:
	if not token_is_valid(jwt):
		return Response('Access denied.', 403)

	try:
		doc = get_document(id)
	except DocumentDoesNotExistError:
		return Response('File not found', 404)

	return doc.get('body', '')


def put_document_contents(jwt: str, id: str) -> Response:
	if not token_is_valid(jwt):
		return Response('Access denied.', 403)

	user_data: dict = users.get_user_data(decode_user_token(jwt).get('username', ''))  # type: ignore

	try:
		update_document(id, None, request.data, user_data=user_data)
	except DocumentDoesNotExistError:
		return Response('File not found', 404)

	return Response('OK')


def get_document_info(jwt: str, id: str):
	if not token_is_valid(jwt):
		return Response('Access denied.', 403)

	try:
		doc = get_document(id)
	except DocumentDoesNotExistError:
		return Response('File not found', 404)

	user_data: dict = users.get_user_data(decode_user_token(jwt).get('username', ''))  # type: ignore

	return jsonify({
		'BaseFileName': doc.get('title', 'Untitled Document'),
		'Size': len(doc.get('body', '')),
		'UserCanWrite': user_data['_id'] == doc['creator'].get('_id'),
	})
