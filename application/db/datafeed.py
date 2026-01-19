"""application.db.datafeed"""

from datetime import datetime

import markdown
from bson.objectid import ObjectId
from pymongo.database import Database

from application.exceptions import (FeedDocumentDoesNotExistError,
                                    FeedDoesNotExistError,
                                    InvalidFeedKindError,
                                    UserDoesNotExistError)

from ..types import Sorting
from . import perms, users

## A pointer to the database object.
db: Database = None  # type: ignore[assignment]


def process_feed(feed: dict) -> dict:
	"""
	Processes a feed dictionary by updating its 'id' and 'creator' fields.

	Args:
		feed (dict): The feed dictionary to be processed. It must contain '_id' and 'creator' keys.

	Returns:
		dict: The processed feed dictionary with 'id' and 'creator' fields updated.

	Raises:
		UserDoesNotExistError: If the user with the given 'creator' ID does not exist.
	"""
	feed['id'] = feed['_id']

	try:
		user_data = users.get_user_by_id(feed['creator'])
		feed['creator'] = user_data['username']
	except UserDoesNotExistError:
		pass

	return feed


def process_document(document: dict, feed_kind: str) -> dict:
	"""
	Processes a document by copying the value of the '_id' key to a new 'id' key.

	Args:
		document (dict): The document to be processed.
		feed_kind (str): The kind of feed the document belongs to, used to generate 'body_html'.

	Returns:
		dict: The processed document with the 'id' key added.
	"""
	document['id'] = document['_id']
	document['body_html'] = get_body_html(feed_kind, document['body'])
	document['html_len'] = len(document['body_html'])
	return document


def get_feed(id: str) -> dict:
	"""
	Retrieve a feed from the database by its ID.

	Args:
		id (str): The ID of the feed to retrieve.

	Returns:
		dict: The processed feed data.

	Raises:
		FeedDoesNotExistError: If the provided ID is not valid or if no feed is found with the given ID.
	"""
	if not ObjectId.is_valid(id):
		raise FeedDoesNotExistError(id)

	feed_data = db.feeds.find_one({'_id': ObjectId(id)})
	if feed_data is None:
		raise FeedDoesNotExistError(id)

	return process_feed(feed_data)


def get_user_feeds(username: str) -> list[dict]:
	"""
	Retrieve the feeds created by a specific user.

	Args:
		username (str): The username of the user whose feeds are to be retrieved.

	Returns:
		list[dict]: A list of dictionaries, each representing a feed created by the user.
	"""
	user_data = users.get_user_data(username)

	return [process_feed(i) for i in db.feeds.find({'creator': user_data['_id']})]


def create_feed(name: str, url: str, kind: str, notify: bool) -> dict:
	"""
	Creates a new feed in the database.

	Args:
		name (str): The name of the feed.
		url (str): The URL of the feed.
		kind (str): The kind of the feed. Must be 'markdown_recursive'.
		notify (bool): Whether to notify users about the feed.

	Returns:
		dict: The created feed data.

	Raises:
		InvalidFeedKindError: If the kind is not 'markdown_recursive'.
	"""
	user_data = perms.caller_info_strict()

	if kind not in ['markdown_recursive']:
		raise InvalidFeedKindError(kind)

	feed = {
		'name': name,
		'url': url,
		'kind': kind,
		'notify': notify,
		'creator': user_data['_id'],
		'created': datetime.utcnow(),
		'inactive': False,
		'current_page': None,
		'current_sort': None,
	}
	id = db.feeds.insert_one(feed).inserted_id
	feed['_id'] = id

	return process_feed(feed)


def delete_feed(id: str) -> dict:
	"""
	Deletes a feed and its associated documents from the database.

	Args:
		id (str): The unique identifier of the feed to be deleted.

	Returns:
		dict: A dictionary representation of the deleted feed after processing.

	Raises:
		FeedDoesNotExistError: If the feed with the given id does not exist.
	"""
	if not ObjectId.is_valid(id):
		raise FeedDoesNotExistError(id)

	feed = db.feeds.find_one({'_id': ObjectId(id)})
	if feed is None:
		raise FeedDoesNotExistError(id)

	# Delete the feed and any associated documents.
	db.feeds.delete_one({'_id': ObjectId(id)})
	db.documents.delete_many({'feed': ObjectId(id)})

	return process_feed(feed)


def get_documents(feed: str, start: int, count: int, sorting: Sorting) -> list[dict]:
	"""
	Retrieve a list of documents from the database based on
	the specified feed, starting index, count, and sorting order.

	Args:
		feed (str): The ID of the feed to retrieve documents from.
		start (int): The starting index of the documents to retrieve.
		count (int): The number of documents to retrieve.
		sorting (Sorting): The sorting criteria for the documents. It should be a dictionary with 'fields'
			as a list of field names and 'descending' as a boolean indicating the sort order.

	Returns:
		list[dict]: A list of documents matching the specified criteria.
			Each document is represented as a dictionary.
	"""
	if not ObjectId.is_valid(feed):
		return []

	feed_data = get_feed(feed)

	return [
		process_document(i, feed_data['kind']) for i in db.documents.find({'feed': ObjectId(feed)}).sort([
			(s, -1 if sorting['descending'] else 1) for s in sorting['fields']
		]).skip(start).limit(count)
	]


def get_document(id: str) -> dict:
	"""
	Retrieve a document from the database by its ID.

	Args:
		id (str): The ID of the document to retrieve.

	Returns:
		dict: The processed document.

	Raises:
		FeedDocumentDoesNotExistError: If the document does not exist or the ID is invalid.
	"""
	if not ObjectId.is_valid(id):
		raise FeedDocumentDoesNotExistError(id)

	document = db.documents.find_one({'_id': ObjectId(id)})

	if document is None:
		raise FeedDocumentDoesNotExistError(id)

	feed = get_feed(document['feed'])

	return process_document(document, feed['kind'])


def count_documents(feed: str) -> int:
	"""
	Count the number of documents in the database for a given feed.

	Args:
		feed (str): The feed identifier, expected to be a valid ObjectId.

	Returns:
		int: The number of documents associated with the given feed. 
			 Returns 0 if the feed identifier is not valid.
	"""
	if not ObjectId.is_valid(feed):
		return 0

	return db.documents.count_documents({'feed': ObjectId(feed)})


def set_feed_notify(id: str, notify: bool) -> dict:
	"""
	Updates the notification setting for a specific feed and returns the updated feed data.

	Args:
		id (str): The unique identifier of the feed.
		notify (bool): The new notification setting for the feed.

	Returns:
		dict: The updated feed data with the new notification setting.
	"""
	feed_data = get_feed(id)
	db.feeds.update_one({'_id': feed_data['_id']}, {'$set': {'notify': notify}})
	feed_data['notify'] = notify
	return feed_data


def get_feeds(start: int, count: int) -> list[dict]:
	"""
	Retrieve a list of processed feeds from the database.

	Args:
		start (int): The starting index from which to retrieve feeds.
		count (int): The number of feeds to retrieve.

	Returns:
		list[dict]: A list of dictionaries, each representing a processed feed.
	"""
	return [
		process_feed(i) for i in db.feeds.find({}).skip(start).limit(count)
	]


def count_feeds() -> int:
	"""
	Count the number of documents in the 'feeds' collection.

	Returns:
		int: The total number of documents in the 'feeds' collection.
	"""
	return db.feeds.count_documents({})


def get_body_html(feed_kind: str, body: str) -> str:
	"""
	Converts the given body text to HTML based on the specified feed kind.

	Args:
		feed_kind (str): The type of feed to process. Currently supports 'markdown_recursive'.
		body (str): The body text to be converted to HTML.

	Returns:
		str: The converted HTML string.

	Raises:
		InvalidFeedKindError: If the provided feed kind is not supported.
	"""
	if feed_kind == 'markdown_recursive':
		body_html = markdown.markdown(body)
	else:
		raise InvalidFeedKindError(feed_kind)

	return body_html


def create_document(feed: str, author: str | None, posted: datetime | None, body: str, title: str | None, url: str) -> dict:
	"""
	Create a new document in the database.

	Args:
		feed (str): The feed identifier.
		author (str | None): The author of the document. Can be None.
		posted (datetime | None): The date and time the document was posted. Can be None.
		body (str): The body content of the document.
		title (str | None): The title of the document. Can be None.
		url (str): The URL of the document.

	Returns:
		dict: The processed document from the database.
	"""
	feed_document = {
		'feed': ObjectId(feed),
		'author': author,
		'posted': posted,
		'title': title,
		'body': body,
		'created': datetime.utcnow(),
		'updated': None,
		'url': url,
		'read': False,
	}
	id = db.documents.insert_one(feed_document).inserted_id
	feed_document['_id'] = id

	feed_data = get_feed(feed)
	return process_document(feed_document, feed_data['kind'])


def update_document(id: str, body: str) -> dict:
	"""
	Update the body of a document in the database.

	Args:
		id (str): The ID of the document to update.
		body (str): The new body content for the document.

	Returns:
		dict: The updated document.
	"""
	document = get_document(id)
	updated = datetime.utcnow()

	db.documents.update_one({'_id': ObjectId(id)}, {'$set': {
		'body': body,
		'updated': updated,
	}})

	feed = get_feed(document['feed'])
	document['body'] = body
	document['body_html'] = get_body_html(feed['kind'], body)
	document['updated'] = updated

	return document


def set_document_read(id: str, read: bool) -> dict:
	"""
	Sets the 'read' status of a document in the database.

	Args:
		id (str): The unique identifier of the document.
		read (bool): The read status to set for the document.

	Returns:
		dict: The updated document with the new 'read' status.
	"""
	document = get_document(id)

	db.documents.update_one({'_id': ObjectId(id)}, {'$set': {'read': read}})
	document['read'] = read

	return document


def set_feed_inactive(id: str, inactive: bool) -> dict:
	"""
	Sets the 'inactive' status of a feed in the database.

	If the feed is set to inactive, new documents will not be fetched and added to the feed.

	Args:
		id (str): The unique identifier of the feed.
		inactive (bool): The status to set for the feed's 'inactive' field.

	Returns:
		dict: The updated feed document with the new 'inactive' status.
	"""
	feed = get_feed(id)
	db.feeds.update_one({'_id': ObjectId(id)}, {'$set': {'inactive': inactive}})
	feed['inactive'] = inactive
	return feed


def set_feed_navigation(id: str, page: int | None, sorting: Sorting | None) -> dict:
	"""
	Updates the navigation settings for a specific feed in the database.

	Args:
		id (str): The unique identifier of the feed.
		page (int | None): The current page number to set for the feed. Can be None.
		sorting (Sorting | None): The sorting criteria to set for the feed. Can be None.

	Returns:
		dict: The updated feed with the new navigation settings.
	"""
	feed = get_feed(id)
	db.feeds.update_one({'_id': ObjectId(id)}, {'$set': {
		'currentPage': page,
		'currentSort': sorting,
	}})
	feed['currentPage'] = page
	feed['currentSort'] = sorting
	return feed
