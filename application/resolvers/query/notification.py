from application.db import perms
from application import exceptions
from application.db.notification import get_public_key, get_subscription, get_subscriptions, get_notifications, count_notifications

def resolve_get_vapid_public_key(_, info) -> str:
	return get_public_key()

@perms.require(['admin'], perform_on_self = True)
def resolve_get_subscriptions(_, info, username: str) -> dict:
	try:
		return { '__typename': 'Subscription', 'list': get_subscriptions(username) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

def resolve_get_subscription(_, info, auth: str) -> dict|None:
	return get_subscription(auth)

@perms.require(['admin'], perform_on_self = True)
def resolve_get_notifications(_, info, username: str, read: bool, start: int, count: int) -> list:
	return get_notifications(username, read, start, count)

@perms.require(['admin'], perform_on_self = True)
def resolve_count_notifications(_, info, username: str, read: bool) -> int:
	return count_notifications(username, read)
