
from flask import Response, jsonify

from application.db.documents import DocumentDoesNotExistError, get_document
from application.tokens import decode_user_token, token_is_valid


def get_document_contents(jwt: str, id: str) -> Response:
	if not token_is_valid(jwt):
		return Response('Access denied.', 403)

	try:
		doc = get_document(id, False)
	except DocumentDoesNotExistError:
		return Response('File not found', 404)

	return doc.get('body', '')


def put_document_contents(jwt: str, id: str) -> Response:
	if not token_is_valid(jwt):
		return Response('Access denied.', 403)

	return Response('OK')


def get_document_info(jwt: str, id: str):
	if not token_is_valid(jwt):
		return Response('Access denied.', 403)

	try:
		doc = get_document(id, False)
	except DocumentDoesNotExistError:
		return Response('File not found', 404)

	return jsonify({
		'BaseFileName': doc.get('title', 'Untitle Document'),
		'Size': len(doc.get('body', '')),
	})
