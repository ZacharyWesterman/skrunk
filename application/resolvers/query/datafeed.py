from application.db.datafeed import get_user_feeds, get_documents, count_documents, get_feed, get_feeds, count_feeds
from application.exceptions import ClientError
from application.objects import Sorting
from application.db import perms
from ..decorators import handle_client_exceptions
from . import query


@query.field('getUserFeeds')
@perms.module('feed')
def resolve_get_user_feeds(_, info, username: str) -> list[dict]:
	try:
		return get_user_feeds(username)
	except ClientError:
		return []


@query.field('getFeedDocuments')
@perms.module('feed')
def resolve_get_feed_documents(_, info, feed: str, start: int, count: int, sorting: Sorting) -> list[dict]:
	return get_documents(feed, start, count, sorting)


@query.field('countFeedDocuments')
@perms.module('feed')
def resolve_count_feed_documents(_, info, feed: str) -> int:
	return count_documents(feed)


@query.field('getFeed')
@perms.module('feed')
@handle_client_exceptions
def resolve_get_feed(_, info, id: str) -> dict:
	return {'__typename': 'Feed', **get_feed(id)}


@query.field('getFeeds')
@perms.module('feed')
def resolve_get_feeds(_, info, start: int, count: int) -> list[dict]:
	return get_feeds(start, count)


@query.field('countFeeds')
@perms.module('feed')
def resolve_count_feeds(_, info) -> int:
	return count_feeds()
