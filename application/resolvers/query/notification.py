from application.db import perms
from application import exceptions
from application.db.notification import get_public_key, get_subscription, get_subscriptions

def resolve_get_vapid_public_key(_, info) -> str:
	return get_public_key()

@perms.require(['admin'], perform_on_self = True)
def resolve_get_subscriptions(_, info, username: str) -> list:
	try:
		return { '__typename': 'Subscription', 'list': get_subscriptions(username) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

def resolve_get_subscription(_, info, auth: str) -> dict|None:
	return get_subscription(auth)
