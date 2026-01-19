"""application.resolvers.query.datafeed"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.datafeed import (count_documents, count_feeds,
                                     get_document, get_documents, get_feed,
                                     get_feeds, get_user_feeds)
from application.exceptions import ClientError, FeedDocumentDoesNotExistError
from application.types import Sorting

from ..decorators import handle_client_exceptions
from . import query


@query.field('getUserFeeds')
@perms.module('feed')
def resolve_get_user_feeds(_, _info: GraphQLResolveInfo, username: str) -> list[dict]:
	"""
	Resolves the GraphQL query to retrieve data feeds for a specified user.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username for which to fetch data feeds.

	Returns:
		list[dict]: A list of data feed dictionaries associated with the user.
			Returns an empty list if a ClientError occurs.
	"""
	try:
		return get_user_feeds(username)
	except ClientError:
		return []


@query.field('getFeedDocuments')
@perms.module('feed')
def resolve_get_feed_documents(
	_,
	_info: GraphQLResolveInfo,
	feed: str,
	start: int,
	count: int,
	sorting: Sorting
) -> list[dict]:
	"""
	Retrieves a list of documents from the specified feed with pagination and sorting.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		feed (str): The name of the feed to retrieve documents from.
		start (int): The starting index for pagination.
		count (int): The number of documents to retrieve.
		sorting (Sorting): Sorting criteria for the documents.

	Returns:
		list[dict]: A list of document dictionaries retrieved from the feed.
	"""
	return get_documents(feed, start, count, sorting)


@query.field('getFeedDocument')
@perms.module('feed')
@handle_client_exceptions
def resolve_get_feed_document(
	_,
	_info: GraphQLResolveInfo,
	id: str
) -> dict:
	"""
	Retrieves a single feed document.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The ID of the feed document.

	Returns:
		dict: A dictionary representing the feed document.
	"""
	return {'__typename': 'FeedDocument', **get_document(id)}


@query.field('getFeedDocumentBodyHtmlChunk')
@perms.module('feed')
def resolve_get_feed_document_chunk(
	_,
	_info: GraphQLResolveInfo,
	id: str,
	start: int,
	count: int
) -> str:
	"""
	Retrieves a chunk of text from a feed document's HTML body.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The ID of the feed document.
		start (int): The index of the first character to fetch.
		count (int): The maximum number of characters to fetch.

	Returns:
		str: A chunk of text at the given position and size.
	"""
	try:
		doc = get_document(id)
	except FeedDocumentDoesNotExistError:
		return ''

	return doc.get('body_html', '')[start:(start + count)]


@query.field('countFeedDocuments')
@perms.module('feed')
def resolve_count_feed_documents(_, _info: GraphQLResolveInfo, feed: str) -> int:
	"""
	Resolves the count of documents for a given feed.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		feed (str): The name or identifier of the feed to count documents for.

	Returns:
		int: The number of documents in the specified feed.
	"""
	return count_documents(feed)


@query.field('getFeed')
@perms.module('feed')
@handle_client_exceptions
def resolve_get_feed(_, _info: GraphQLResolveInfo, id: str) -> dict:
	"""
	Resolves the GraphQL query for fetching a feed by its ID.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the feed to retrieve.

	Returns:
		dict: A dictionary representing the feed.
	"""
	return {'__typename': 'Feed', **get_feed(id)}


@query.field('getFeeds')
@perms.module('feed')
def resolve_get_feeds(_, _info: GraphQLResolveInfo, start: int, count: int) -> list[dict]:
	"""
	Resolves the GraphQL query for retrieving a list of data feeds.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		start (int): The starting index for fetching feeds.
		count (int): The number of feeds to retrieve.

	Returns:
		list[dict]: A list of dictionaries representing the data feeds.
	"""
	return get_feeds(start, count)


@query.field('countFeeds')
@perms.module('feed')
def resolve_count_feeds(_, _info: GraphQLResolveInfo) -> int:
	"""
	Resolves the total number of data feeds for the calling user.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		int: The count of data feeds.
	"""
	return count_feeds()
