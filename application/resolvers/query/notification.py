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
	return get_public_key()


@query.field('getSubscriptions')
@perms.require('admin', perform_on_self=True)
@handle_client_exceptions
def resolve_get_subscriptions(_, _info: GraphQLResolveInfo, username: str) -> dict:
	return {'__typename': 'Subscription', 'list': get_subscriptions(username)}


@query.field('getSubscription')
def resolve_get_subscription(_, _info: GraphQLResolveInfo, auth: str) -> dict | None:
	return get_subscription(auth)


@query.field('getNotifications')
@perms.require('admin', perform_on_self=True)
def resolve_get_notifications(_, _info: GraphQLResolveInfo, username: str, read: bool, start: int, count: int) -> list:
	return get_notifications(username, read, start, count)


@query.field('countNotifications')
@perms.require('admin', perform_on_self=True)
def resolve_count_notifications(_, _info: GraphQLResolveInfo, username: str, read: bool) -> int:
	return count_notifications(username, read)
