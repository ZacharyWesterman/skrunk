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
def resolve_create_feed(_, _info: GraphQLResolveInfo, name: str, url: str, kind: str, notify: bool) -> dict:
	return {'__typename': 'Feed', **create_feed(name, url, kind, notify)}


@mutation.field('deleteFeed')
@perms.module('feed')
@handle_client_exceptions
@perms.require('admin', perform_on_self=True, data_func=get_feed)
def resolve_delete_feed(_, _info: GraphQLResolveInfo, id: str) -> dict:
	return {'__typename': 'Feed', **delete_feed(id)}


@mutation.field('updateFeedNotify')
@perms.module('feed')
@perms.require('admin', perform_on_self=True, data_func=get_feed)
@handle_client_exceptions
def resolve_update_feed_notify(_, _info: GraphQLResolveInfo, id: str, notify: bool) -> dict:
	return {'__typename': 'Feed', **set_feed_notify(id, notify)}


@mutation.field('createFeedDocument')
@perms.module('feed')
@perms.require('edit')
@handle_client_exceptions
def resolve_create_feed_document(_, _info: GraphQLResolveInfo, feed: str, author: str | None, posted: datetime | None, body: str, title: str | None, url: str) -> dict:
	return {'__typename': 'FeedDocument', **create_document(feed, author, posted, body, title, url)}


@mutation.field('updateFeedDocument')
@perms.module('feed')
@perms.require('edit')
@handle_client_exceptions
def resolve_update_feed_document(_, _info: GraphQLResolveInfo, id: str, body: str) -> dict:
	return {'__typename': 'FeedDocument', **update_document(id, body)}


@mutation.field('markDocumentRead')
@perms.module('feed')
@perms.require('edit')
@handle_client_exceptions
def resolve_mark_document_read(_, _info: GraphQLResolveInfo, id: str, read: bool) -> dict:
	return {'__typename': 'FeedDocument', **set_document_read(id, read)}


@mutation.field('setFeedInactive')
@perms.module('feed')
@perms.require('edit')
@handle_client_exceptions
def resolve_set_feed_inactive(_, _info: GraphQLResolveInfo, id: str, inactive: bool) -> dict:
	return {'__typename': 'Feed', **set_feed_inactive(id, inactive)}


@mutation.field('setFeedNavigation')
@perms.module('feed')
@perms.require('edit')
@handle_client_exceptions
def resolve_set_feed_navigation(_, _info: GraphQLResolveInfo, id: str, page: int | None, sorting: Sorting | None) -> dict:
	return {'__typename': 'Feed', **set_feed_navigation(id, page, sorting)}
