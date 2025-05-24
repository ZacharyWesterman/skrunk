"""application.resolvers.mutation.notification"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.notification import (create_subscription,
                                         delete_subscription,
                                         delete_subscriptions,
                                         get_user_from_notif, mark_all_as_read,
                                         mark_as_read, send)

from ..decorators import *
from . import mutation


@mutation.field('createSubscription')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_create_subscription(_, info: GraphQLResolveInfo, username: str, subscription: dict) -> dict:
	create_subscription(username, subscription)
	return {'__typename': 'Notification', 'message': 'Subscription created successfully'}


@mutation.field('deleteSubscription')
def resolve_delete_subscription(_, info: GraphQLResolveInfo, auth: str) -> int:
	return delete_subscription(auth)


@mutation.field('deleteSubscriptions')
@perms.require('admin', perform_on_self=True)
def resolve_delete_subscriptions(_, info: GraphQLResolveInfo, username: str) -> int:
	return delete_subscriptions(username)


@mutation.field('sendNotification')
@perms.require('admin', 'notify')
@handle_client_exceptions
def resolve_send_notification(_, info: GraphQLResolveInfo, username: str, title: str, body: str, category: str) -> dict:
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
def resolve_send_notification_as_read(_, info: GraphQLResolveInfo, username: str, title: str, body: str, category: str) -> dict:
	if title == '':
		return {'__typename': 'BadNotification', 'message': 'Notification title cannot be blank'}

	if category == '' or category is None:
		notif = send(title, body, username, read=True)
	else:
		notif = send(title, body, username, category=category, read=True)

	return {'__typename': 'Notification', **notif}


@mutation.field('markNotifAsRead')
@perms.require('admin', perform_on_self=True, data_func=get_user_from_notif)
def resolve_mark_notification_as_read(_, info: GraphQLResolveInfo, id: str) -> bool:
	mark_as_read(id)
	return True


@mutation.field('markAllNotifsAsRead')
@perms.require('admin', perform_on_self=True)
def resolve_mark_all_notifications_as_read(_, info: GraphQLResolveInfo, username: str) -> bool:
	mark_all_as_read(username)
	return True
