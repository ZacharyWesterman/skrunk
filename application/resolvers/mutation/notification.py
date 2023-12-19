from application.db import perms
from application import exceptions
from application.db.notification import create_subscription, delete_subscription, delete_subscriptions, send

@perms.require(['admin'], perform_on_self = True)
def resolve_create_subscription(_, info, username: str, subscription: dict) -> dict:
	try:
		create_subscription(username, subscription)
		return { '__typename': 'Notification', 'message': 'Subscription created successfully' }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

def resolve_delete_subscription(_, info, p256dh: str) -> int:
	return delete_subscription(p256dh)

@perms.require(['admin'], perform_on_self = True)
def resolve_delete_subscriptions(_, info, username: str) -> int:
	return delete_subscriptions(username)

@perms.require(['admin'])
def resolve_send_notification(_, info, username: str, message: str, category: str) -> dict:
	if message == '':
		return { '__typename': 'BadNotification', 'message': 'Notification message cannot be blank'}

	try:
		if category == '' or category is None:
			send(message, username)
		else:
			send(message, username, category = category)

		return { '__typename': 'Notification', 'message': 'Notification sent' }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }
