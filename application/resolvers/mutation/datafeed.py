"""application.resolvers.mutation.datafeed"""

from datetime import datetime

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.datafeed import (create_document, create_feed, delete_feed,
                                     get_feed, set_document_read,
                                     set_feed_inactive, set_feed_navigation,
                                     set_feed_notify, update_document)
from application.types import Sorting

from ..decorators import handle_client_exceptions
from . import mutation


@mutation.field('createFeed')
@perms.module('feed')
@handle_client_exceptions
def resolve_create_feed(
	_,
	_info: GraphQLResolveInfo,
	name: str,
	url: str,
	kind: str,
	notify: bool
) -> dict:
	"""
	Creates a new feed with the specified parameters.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		name (str): The name of the feed to create.
		url (str): The URL associated with the feed.
		kind (str): The type or category of the feed.
		notify (bool): Whether to enable notifications for the feed.

	Returns:
		dict: A dictionary representing the newly created feed.
	"""
	return {'__typename': 'Feed', **create_feed(name, url, kind, notify)}


@mutation.field('deleteFeed')
@perms.module('feed')
@handle_client_exceptions
@perms.require('admin', perform_on_self=True, data_func=get_feed)
def resolve_delete_feed(_, _info: GraphQLResolveInfo, id: str) -> dict:
	"""
	Deletes a feed by its ID.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the feed to delete.

	Returns:
		dict: A dictionary representing the deleted feed.
	"""
	return {'__typename': 'Feed', **delete_feed(id)}


@mutation.field('updateFeedNotify')
@perms.module('feed')
@perms.require('admin', perform_on_self=True, data_func=get_feed)
@handle_client_exceptions
def resolve_update_feed_notify(_, _info: GraphQLResolveInfo, id: str, notify: bool) -> dict:
	"""
	Updates the notification setting for a feed.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the feed to update.
		notify (bool): The new notification setting for the feed.

	Returns:
		dict: A dictionary representing the updated feed.
	"""
	return {'__typename': 'Feed', **set_feed_notify(id, notify)}


@mutation.field('createFeedDocument')
@perms.module('feed')
@perms.require('edit')
@handle_client_exceptions
def resolve_create_feed_document(_, _info: GraphQLResolveInfo, feed: str, author: str | None, posted: datetime | None, body: str, title: str | None, url: str) -> dict:
	"""
	Creates a new feed document and returns its representation.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		feed (str): The identifier or name of the feed to which the document belongs.
		author (str | None): The author of the document, or None if not specified.
		posted (datetime | None): The datetime when the document was posted, or None if not specified.
		body (str): The main content of the feed document.
		title (str | None): The title of the document, or None if not specified.
		url (str): The URL associated with the feed document.

	Returns:
		dict: A dictionary representing the created feed document.
	"""
	return {'__typename': 'FeedDocument', **create_document(feed, author, posted, body, title, url)}


@mutation.field('updateFeedDocument')
@perms.module('feed')
@perms.require('edit')
@handle_client_exceptions
def resolve_update_feed_document(_, _info: GraphQLResolveInfo, id: str, body: str) -> dict:
	"""
	Updates a feed document with the given ID and body.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the feed document to update.
		body (str): The new content for the feed document.

	Returns:
		dict: A dictionary representing the updated feed document.
	"""
	return {'__typename': 'FeedDocument', **update_document(id, body)}


@mutation.field('markDocumentRead')
@perms.module('feed')
@perms.require('edit')
@handle_client_exceptions
def resolve_mark_document_read(_, _info: GraphQLResolveInfo, id: str, read: bool) -> dict:
	"""
	Marks a document as read or unread in the data feed.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the document to be marked.
		read (bool): Flag indicating whether the document should be
			marked as read (True) or unread (False).

	Returns:
		dict: A dictionary representing the updated FeedDocument.
	"""
	return {'__typename': 'FeedDocument', **set_document_read(id, read)}


@mutation.field('setFeedInactive')
@perms.module('feed')
@perms.require('edit')
@handle_client_exceptions
def resolve_set_feed_inactive(_, _info: GraphQLResolveInfo, id: str, inactive: bool) -> dict:
	"""
	Marks a feed as inactive or active.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the feed to update.
		inactive (bool): Flag indicating whether to set the feed as inactive (True) or active (False).

	Returns:
		dict: A dictionary representing the updated feed object.
	"""
	return {'__typename': 'Feed', **set_feed_inactive(id, inactive)}


@mutation.field('setFeedNavigation')
@perms.module('feed')
@perms.require('edit')
@handle_client_exceptions
def resolve_set_feed_navigation(
	_,
	_info: GraphQLResolveInfo,
	id: str,
	page: int | None,
	sorting: Sorting | None
) -> dict:
	"""
	Set the navigation state for a feed, including the current page and sorting options.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the feed.
		page (int | None): The page number to navigate to, or None to use the default.
		sorting (Sorting | None): The sorting configuration for the feed, or None for default sorting.

	Returns:
		dict: A dictionary representing the updated feed navigation state.
	"""
	return {'__typename': 'Feed', **set_feed_navigation(id, page, sorting)}
