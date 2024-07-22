from . import users, perms
from datetime import datetime
from application.exceptions import InvalidFeedKindError

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
