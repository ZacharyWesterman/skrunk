from . import users, perms
from datetime import datetime
from application.exceptions import InvalidFeedKindError, FeedDoesNotExistError
from bson.objectid import ObjectId
from ..objects import Sorting

from pymongo.database import Database
db: Database = None

def prepare_feed(feed: dict) -> dict:
	feed['id'] = feed['_id']
	return feed

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
		i for i in db.documents.find({'feed': ObjectId(feed)}).sort([
			(s, -1 if sorting['descending'] else 1) for s in sorting['fields']
		]).skip(start).limit(count)
	]

def count_documents(feed: str) -> int:
	if not ObjectId.is_valid(feed):
		return 0

	return db.documents.count_documents({'feed': ObjectId(feed)})
