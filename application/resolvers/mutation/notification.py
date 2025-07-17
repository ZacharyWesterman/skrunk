"""application.resolvers.mutation.notification"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.notification import (create_subscription,
                                         delete_subscription,
                                         delete_subscriptions,
                                         get_user_from_notif, mark_all_as_read,
                                         mark_as_read, send)

from ..decorators import handle_client_exceptions
from . import mutation


@mutation.field('createSubscription')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_create_subscription(_, _info: GraphQLResolveInfo, username: str, subscription: dict) -> dict:
	"""
	Creates a new subscription for a given user.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user for whom the subscription is being created.
		subscription (dict): A dictionary containing subscription details.

	Returns:
		dict: A notification response indicating successful creation.
	"""
	create_subscription(username, subscription)
	return {'__typename': 'Notification', 'message': 'Subscription created successfully'}


@mutation.field('deleteSubscription')
def resolve_delete_subscription(_, _info: GraphQLResolveInfo, auth: str) -> int:
	"""
	Deletes one or more subscriptions with the given authentication token.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		auth (str): Authentication token or identifier for the subscription to be deleted.

	Returns:
		int: The number of subscriptions deleted.
	"""
	return delete_subscription(auth)


@mutation.field('deleteSubscriptions')
@perms.require('admin', perform_on_self=True)
def resolve_delete_subscriptions(_, _info: GraphQLResolveInfo, username: str) -> int:
	"""
	Deletes all subscriptions associated with the specified username.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username whose subscriptions are to be deleted.

	Returns:
		int: The number of subscriptions deleted.
	"""
	return delete_subscriptions(username)


@mutation.field('sendNotification')
@perms.require('admin', 'notify')
@handle_client_exceptions
def resolve_send_notification(
	_,
    _info: GraphQLResolveInfo,
    username: str,
    title: str,
    body: str,
    category: str
) -> dict:
	"""
	Sends a notification to a specified user with the given title, body, and optional category.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the recipient.
		title (str): The title of the notification.
		body (str): The body content of the notification.
		category (str): The category of the notification.
			If empty or None, the notification is sent without a category.

	Returns:
		dict: A dictionary representing the result of the operation.
			Returns a 'BadNotification' type with an error message if information is missing or invalid,
			otherwise returns a 'Notification' type with the notification details.
	"""
	if title == '':
		return {'__typename': 'BadNotification', 'message': 'Notification title cannot be blank'}

	if category == '' or category is None:
		notif = send(title, body, username)
	else:
		notif = send(title, body, username, category=category)

	return {'__typename': 'Notification', **notif}


@mutation.field('sendNotificationAsRead')
@perms.require('admin', 'notify')
@handle_client_exceptions
def resolve_send_notification_as_read(
	_,
    _info: GraphQLResolveInfo,
    username: str,
    title: str,
    body: str,
    category: str
) -> dict:
	"""
	Marks a notification as read and sends it to the specified user.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the recipient.
		title (str): The title of the notification.
		body (str): The body content of the notification.
		category (str): The category of the notification.
			If empty or None, the notification is sent without a category.

	Returns:
		dict: A dictionary representing the result of the operation.
			Returns a 'BadNotification' type with an error message if information is missing or invalid,
			otherwise returns a 'Notification' type with the notification details.
	"""
	if title == '':
		return {'__typename': 'BadNotification', 'message': 'Notification title cannot be blank'}

	if category == '' or category is None:
		notif = send(title, body, username, read=True)
	else:
		notif = send(title, body, username, category=category, read=True)

	return {'__typename': 'Notification', **notif}


@mutation.field('markNotifAsRead')
@perms.require('admin', perform_on_self=True, data_func=get_user_from_notif)
def resolve_mark_notification_as_read(_, _info: GraphQLResolveInfo, id: str) -> bool:
	"""
	Marks a notification as read by its ID.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		id (str): The unique identifier of the notification to mark as read.

	Returns:
		bool: True if the notification was successfully marked as read.
	"""
	mark_as_read(id)
	return True


@mutation.field('markAllNotifsAsRead')
@perms.require('admin', perform_on_self=True)
def resolve_mark_all_notifications_as_read(_, _info: GraphQLResolveInfo, username: str) -> bool:
	"""
	Marks all notifications as read for the specified user.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		username (str): The username of the user whose notifications will be marked as read.

	Returns:
		bool: True if the operation was successful.
	"""
	mark_all_as_read(username)
	return True
