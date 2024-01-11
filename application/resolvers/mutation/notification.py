from application.db import perms
from application import exceptions
from application.db.notification import create_subscription, delete_subscription, delete_subscriptions, send, mark_as_read, get_user_from_notif, mark_all_as_read

@perms.require(['admin'], perform_on_self = True)
def resolve_create_subscription(_, info, username: str, subscription: dict) -> dict:
	try:
		create_subscription(username, subscription)
		return { '__typename': 'Notification', 'message': 'Subscription created successfully' }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

def resolve_delete_subscription(_, info, auth: str) -> int:
	return delete_subscription(auth)

@perms.require(['admin'], perform_on_self = True)
def resolve_delete_subscriptions(_, info, username: str) -> int:
	return delete_subscriptions(username)

@perms.require(['admin', 'notify'])
def resolve_send_notification(_, info, username: str, title: str, body: str, category: str) -> dict:
	if title == '':
		return { '__typename': 'BadNotification', 'message': 'Notification title cannot be blank'}

	try:
		if category == '' or category is None:
			send(title, body, username)
		else:
			send(title, body, username, category = category)

		return { '__typename': 'Notification', 'message': 'Notification sent' }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['admin'], perform_on_self=True, data_func=get_user_from_notif)
def resolve_mark_notification_as_read(_, info, id: str) -> bool:
	mark_as_read(id)
	return True

@perms.require(['admin'], perform_on_self=True)
def resolve_mark_all_notifications_as_read(_, info, username: str) -> bool:
	mark_all_as_read(username)
	return True
