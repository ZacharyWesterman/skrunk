"""Allows users to create, read and edit arbitrary rich text documents."""

from datetime import UTC, datetime

import markdown
from bson.objectid import ObjectId
from pymongo.collection import Collection

from application.exceptions import (DocumentDoesNotExistError,
                                    UserDoesNotExistError)

from . import perms, settings, users

## A pointer to the Documents collection in the database.
db: Collection = None  # type: ignore[assignment]


def parse_document(doc: dict) -> dict:
	"""
	Parses a document from the database.

	Args:
		doc (dict): The document to parse.

	Returns:
		dict: The parsed document.
	"""

	doc['id'] = str(doc['_id'])

	try:
		doc['creator'] = users.get_user_by_id(doc['creator'])
	except UserDoesNotExistError:
		doc['creator'] = {
			'username': doc['creator'],
			'display_name': doc['creator'],
		}

	if doc['updater'] is not None:
		try:
			doc['updater'] = users.get_user_by_id(doc['updater'])
		except UserDoesNotExistError:
			doc['updater'] = {
				'username': doc['updater'],
				'display_name': doc['updater'],
			}

	if settings.get_config('wopi:url'):
		doc['body_html'] = ''
	else:
		doc['body_html'] = markdown.markdown(doc['body'])

	return doc


def get_document(id: str) -> dict:
	"""
	Retrieves a document from the database by its ID.

	Args:
		id (str): The ID of the document to retrieve.

	Returns:
		dict: The document.
	"""
	if doc := db.find_one({'_id': ObjectId(id)}):
		return parse_document(doc)

	raise DocumentDoesNotExistError(id)


def get_documents(start: int, count: int) -> list:
	"""
	Retrieves a list of documents.

	Args:
		start (int): The starting index for pagination.
		count (int): The number of books to retrieve.

	Returns:
		list: A list of documents.
	"""

	selection = db.find({'history': False}).skip(start).limit(count).sort((('updated', -1), ('created', -1)))

	return [parse_document(doc) for doc in selection]


def create_document(title: str, body: str) -> dict:
	"""
	Creates a new document in the database.

	Args:
		title (str): The title of the document.
		body (str): The content of the document.
		parent (str | None, optional): The ID of the parent document. Defaults to None.

	Returns:
		dict: The new document.
	"""

	caller = perms.caller_info_strict()

	body_text: str | bytes = body

	if body == '' and settings.get_config('wopi:url'):
		with open('data/empty.odt', 'rb') as fp:
			body_text = fp.read()

	doc = {
		'title': title,
		'body': body_text,
		'creator': caller.get('_id'),
		'created': datetime.now(UTC),
		'updated': None,
		'updater': None,
		'parent': None,
		'hidden': False,
		'draft': False,
		'history': False,
		'previous': None,
		'tags': [],
	}

	if doc['creator'] is None:
		doc['creator'] = caller.get('username')

	doc_id = db.insert_one(doc).inserted_id
	doc['_id'] = doc_id

	return parse_document(doc)


def update_document(doc_id: str, title: str | None, body: str | bytes | None, *, user_data: dict | None = None) -> dict:
	"""
	Updates a document in the database.

	Args:
		doc_id (str): The ID of the document to update.
		title (str | None): The new title of the document. If None, the title is not updated.
		body (str | None): The new content of the document. If None, the body is not updated.

	Returns:
		dict: The updated document.
	"""

	if (doc := db.find_one({'_id': ObjectId(doc_id)})) is None:
		raise DocumentDoesNotExistError(doc_id)

	if title is None and body is None:
		# No change
		return parse_document(doc)

	if title == doc['title'] and body == doc['body']:
		# No change
		return parse_document(doc)

	user_id: ObjectId = (perms.caller_info_strict() if user_data is None else user_data).get('_id')  # type: ignore

	# prev_doc = {
	# 	**doc,
	# 	'history': True,
	# 	'parent': ObjectId(doc_id),
	# }
	# del prev_doc['_id']
	# prev_id = db.insert_one(prev_doc).inserted_id

	# doc['previous'] = prev_id

	doc['updated'] = datetime.now(UTC)
	doc['updater'] = user_id

	if title is not None:
		doc['title'] = title
	if body is not None:
		doc['body'] = body

	db.update_one({'_id': ObjectId(doc_id)}, {'$set': doc})

	return parse_document(doc)


def delete_document(doc_id: str) -> dict:
	"""
	Deletes a document from the database.

	Any history items get deleted.

	Args:
		doc_id (str): The ID of the document to delete.

	Returns:
		dict: The deleted document, if successful.
	"""

	id = ObjectId(doc_id)

	doc = db.find_one({'_id': id})
	if doc is None:
		raise DocumentDoesNotExistError(doc_id)

	db.delete_many({'parent': id})
	db.delete_one({'_id': id})

	return parse_document(doc)
