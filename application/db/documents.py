"""Allows users to create, read and edit arbitrary rich text documents."""

from datetime import UTC, datetime

import markdown
from bson.objectid import ObjectId
from pymongo.collection import Collection

from application.exceptions import (DocumentDoesNotExistError,
                                    UserDoesNotExistError)

from . import perms, users

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

	doc['body_html'] = markdown.markdown(doc['body'])

	return doc


def get_document(doc_id: str) -> dict:
	"""
	Retrieves a document from the database by its ID.

	Args:
		doc_id (str): The ID of the document to retrieve.

	Returns:
		dict: The document.
	"""
	if doc := db.find_one({'_id': ObjectId(doc_id)}):
		return parse_document(doc)

	raise DocumentDoesNotExistError(doc_id)


def get_child_documents(doc_id: str | None) -> list:
	"""
	Retrieves the child documents of a document.

	Args:
		doc_id (str | None): The optional ID of the document. If None, retrieves top-level documents.

	Returns:
		list: The child documents.
	"""

	selection = db.find({'parent': ObjectId(doc_id)}) if doc_id else db.find({'parent': None})

	return [parse_document(doc) for doc in selection]


def create_document(title: str, body: str, parent: str | None = None) -> dict:
	"""
	Creates a new document in the database.

	Args:
		title (str): The title of the document.
		body (str): The content of the document.
		parent (str | None, optional): The ID of the parent document. Defaults to None.

	Returns:
		dict: The new document.
	"""

	doc = {
		'title': title,
		'body': body,
		'creator': perms.caller_info_strict().get('username'),
		'created': datetime.now(UTC),
		'updated': None,
		'updater': None,
		'parent': ObjectId(parent) if parent else None,
		'hidden': False,
		'draft': False,
		'tags': [],
		'keywords': [],
		'history': [],
	}

	doc_id = db.insert_one(doc).inserted_id
	doc['_id'] = doc_id

	return parse_document(doc)


def update_document(doc_id: str, title: str | None, body: str | None, new_parent: str | None) -> dict:
	"""
	Updates a document in the database.

	Args:
		doc_id (str): The ID of the document to update.
		title (str | None): The new title of the document. If None, the title is not updated.
		body (str | None): The new content of the document. If None, the body is not updated.
		new_parent (str | None): The ID of the new parent document. If None, the parent is not updated.

	Returns:
		dict: The updated document.
	"""

	if (doc := db.find_one({'_id': ObjectId(doc_id)})) is None:
		raise DocumentDoesNotExistError(doc_id)

	if title or body or new_parent:

		username: str = perms.caller_info_strict().get('username', '')
		user_data = users.get_user_data(username)

		prev_doc = {
			'updated': doc['updated'],
			'updater': user_data['_id'],
			'title': None,
			'body': None,
			'parent': None,
		}

		if title is not None:
			prev_doc['title'] = doc['title']
			doc['title'] = title

		if body is not None:
			prev_doc['body'] = doc['body']
			doc['body'] = body

		if new_parent is not None:
			prev_doc['parent'] = doc['parent']
			doc['parent'] = ObjectId(new_parent)

		doc['updated'] = datetime.now(UTC)
		doc['history'].append(prev_doc)

		db.update_one({'_id': ObjectId(doc_id)}, {'$set': doc})

	return parse_document(doc)


def delete_document(doc_id: str) -> dict:
	"""
	Deletes a document from the database.

	Args:
		doc_id (str): The ID of the document to delete.

	Returns:
		dict: The deleted document.
	"""

	if doc := db.find_one({'_id': ObjectId(doc_id)}):
		db.delete_one({'_id': ObjectId(doc_id)})
		return parse_document(doc)

	raise DocumentDoesNotExistError(doc_id)
