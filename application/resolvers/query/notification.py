"""application.resolvers.query.notification"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.notification import (count_notifications,
                                         get_notifications, get_public_key,
                                         get_subscription, get_subscriptions)

from ..decorators import handle_client_exceptions
from . import query


@query.field('getVAPIDPublicKey')
def resolve_get_vapid_public_key(_, _info: GraphQLResolveInfo) -> str:
	"""
	Resolves the GraphQL query for retrieving the VAPID public key.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		str: The VAPID public key as a string.
	"""
	return get_public_key()


@query.field('getSubscriptions')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_get_subscriptions(_, _info: GraphQLResolveInfo, username: str) -> dict:
	"""
	Resolves the GraphQL query for retrieving a user's subscriptions.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username for which to fetch subscriptions.

	Returns:
		dict: A dictionary containing the typename and a list of subscriptions for the specified user.
	"""
	return {'__typename': 'Subscription', 'list': get_subscriptions(username)}


@query.field('getSubscription')
def resolve_get_subscription(_, _info: GraphQLResolveInfo, auth: str) -> dict | None:
	"""
	Resolves the retrieval of a subscription based on the provided authentication token.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		auth (str): Authentication token used to identify the subscription.

	Returns:
		dict | None: The subscription data if found, otherwise None.
	"""
	return get_subscription(auth)


@query.field('getNotifications')
@perms.require('admin', perform_on_self=True)
def resolve_get_notifications(_, _info: GraphQLResolveInfo, username: str, read: bool, start: int, count: int) -> list:
	"""
	Resolves the retrieval of notifications for a given user.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username for which to fetch notifications.
		read (bool): Filter notifications by their read status.
		start (int): The starting index for pagination.
		count (int): The number of notifications to retrieve.

	Returns:
		list: A list of notifications matching the criteria.
	"""
	return get_notifications(username, read, start, count)


@query.field('countNotifications')
@perms.require('admin', perform_on_self=True)
def resolve_count_notifications(_, _info: GraphQLResolveInfo, username: str, read: bool) -> int:
	"""
	Resolves the count of notifications for a given user based on their read status.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user whose notifications are being counted.
		read (bool): The read status to filter notifications (True for read, False for unread).

	Returns:
		int: The number of notifications matching the specified criteria.
	"""
	return count_notifications(username, read)
