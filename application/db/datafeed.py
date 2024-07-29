from . import users, perms
from datetime import datetime
from application.exceptions import InvalidFeedKindError, FeedDoesNotExistError, UserDoesNotExistError, FeedDocumentDoesNotExistError
from bson.objectid import ObjectId
from ..objects import Sorting
import markdown

from pymongo.database import Database
db: Database = None

def prepare_feed(feed: dict) -> dict:
	feed['id'] = feed['_id']

	try:
		user_data = users.get_user_by_id(feed['creator'])
		feed['creator'] = user_data['username']
	except UserDoesNotExistError:
		pass

	return feed

def prepare_document(document: dict) -> dict:
	document['id'] = document['_id']
	return document

def get_feed(id: str) -> dict:
	if not ObjectId.is_valid(id):
		raise FeedDoesNotExistError(id)

	feed_data = db.feeds.find_one({'_id': ObjectId(id)})
	if feed_data is None:
		raise FeedDoesNotExistError(id)

	return prepare_feed(feed_data)

def get_user_feeds(username: str) -> list[dict]:
	user_data = users.get_user_data(username)

	return [prepare_feed(i) for i in db.feeds.find({'creator': user_data['_id']})]

def create_feed(name: str, url: str, kind: str, notify: bool) -> dict:
	user_data = perms.caller_info()

	if kind not in ['markdown_recursive']:
		raise InvalidFeedKindError(kind)

	id = db.feeds.insert_one({
		'name': name,
		'url': url,
		'kind': kind,
		'notify': notify,
		'creator': user_data['_id'],
		'created': datetime.utcnow(),
		'inactive': False,
		'current_page': None,
		'current_sort': None,
	}).inserted_id

	return prepare_feed(db.feeds.find_one({'_id':id}))

def delete_feed(id: str) -> dict:
	if not ObjectId.is_valid(id):
		raise FeedDoesNotExistError(id)

	feed = db.feeds.find_one({'_id': ObjectId(id)})
	if feed is None:
		raise FeedDoesNotExistError(id)

	#Delete the feed and any associated documents.
	db.feeds.delete_one({'_id': ObjectId(id)})
	db.documents.delete_many({'feed': ObjectId(id)})

	return prepare_feed(feed)

def get_documents(feed: str, start: int, count: int, sorting: Sorting) -> list[dict]:
	if not ObjectId.is_valid(feed):
		return []

	return [
		prepare_document(i) for i in db.documents.find({'feed': ObjectId(feed)}).sort([
			(s, -1 if sorting['descending'] else 1) for s in sorting['fields']
		]).skip(start).limit(count)
	]

def get_document(id: str) -> dict:
	if not ObjectId.is_valid(id):
		raise FeedDocumentDoesNotExistError(id)

	document = db.documents.find_one({'_id': ObjectId(id)})

	if document is None:
		raise FeedDocumentDoesNotExistError(id)

	return prepare_document(document)

def count_documents(feed: str) -> int:
	if not ObjectId.is_valid(feed):
		return 0

	return db.documents.count_documents({'feed': ObjectId(feed)})

def set_feed_notify(id: str, notify: bool) -> dict:
	feed_data = get_feed(id)
	db.feeds.update_one({'_id': feed_data['_id']}, {'$set': {'notify': notify}})
	feed_data['notify'] = notify
	return feed_data

def get_feeds(start: int, count: int) -> list[dict]:
	return [
		prepare_feed(i) for i in db.feeds.find({}).skip(start).limit(count)
	]

def count_feeds() -> int:
	return db.feeds.count_documents({})

def get_body_html(feed_kind: str, body: str) -> str:
	if feed_kind == 'markdown_recursive':
		body_html = markdown.markdown(body)
	else:
		raise InvalidFeedKindError(feed_kind) #Should never happen, but we want the caller to know about it if it does happen!

	return body_html

def create_document(feed: str, author: str|None, posted: datetime|None, body: str, title: str|None, url: str) -> dict:
	feed_data = get_feed(feed)

	id = db.documents.insert_one({
		'feed': ObjectId(feed),
		'author': author,
		'posted': posted,
		'title': title,
		'body': body,
		'body_html': get_body_html(feed_data['kind'], body),
		'created': datetime.utcnow(),
		'updated': None,
		'url': url,
		'read': False,
	}).inserted_id

	return prepare_document(db.documents.find_one({'_id': id}))

def update_document(id: str, body: str) -> dict:
	document = get_document(id)

	feed = get_feed(document['feed'])
	body_html = get_body_html(feed['kind'], body)
	updated = datetime.utcnow()

	db.documents.update_one({'_id': ObjectId(id)}, {'$set': {
		'body': body,
		'body_html': body_html,
		'updated': updated,
	}})

	document['body'] = body
	document['body_html'] = body_html
	document['updated'] = updated

	return document

def set_document_read(id: str, read: bool) -> dict:
	document = get_document(id)

	db.documents.update_one({'_id': ObjectId(id)}, {'$set': {'read': read}})
	document['read'] = read

	return document

def set_feed_inactive(id: str, inactive: bool) -> dict:
	feed = get_feed(id)
	db.feeds.update_one({'_id': ObjectId(id)}, {'$set': {'inactive': inactive}})
	feed['inactive'] = inactive
	return feed

def set_feed_navigation(id: str, page: int|None, sorting: Sorting|None) -> dict:
	feed = get_feed(id)
	db.feeds.update_one({'_id': ObjectId(id)}, {'$set': {
		'currentPage': page,
		'currentSort': sorting,
	}})
	feed['currentPage'] = page
	feed['currentSort'] = sorting
	return feed
