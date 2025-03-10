"""application.db.notification"""

from application.db import settings, users
from application.db.sessions import get_first_session_token
from application import exceptions
from pywebpush import webpush, WebPushException
from urllib.parse import urlsplit
from datetime import datetime
from bson.objectid import ObjectId
import json

# Attempt to read the VAPID keys from the data directory.
try:
	## The VAPID private key used for sending notifications.
	VAPID_PRIVATE_KEY = open('data/private_key.txt', 'r+').readline().strip('\n')

	## The VAPID public key used for sending notifications.
	VAPID_PUBLIC_KEY = open('data/public_key.txt', 'r+').read().strip('\n')
except FileNotFoundError:
	print('WARNING: No VAPID keys found!', ' ', '\n', None, True)

from pymongo.database import Database

## A pointer to the database object.
db: Database = None


def get_user_from_notif(id: str) -> dict:
	"""
	Retrieve user information based on a notification ID.

	Args:
		id (str): The ID of the notification.

	Returns:
		dict: A dictionary containing user information if found, otherwise an empty dictionary.
	"""
	notif = db.notif_log.find_one({'_id': ObjectId(id)})
	if notif is None:
		return {}

	return users.get_user_by_id(notif.get('recipient'))


def get_public_key() -> str:
	"""
	Retrieve the VAPID public key.

	Returns:
		str: The VAPID public key as a string.
	"""
	return VAPID_PUBLIC_KEY


def get_subscriptions(username: str) -> list:
	"""
	Retrieve a list of notification subscription tokens for a given user.

	Args:
		username (str): The username of the user whose subscriptions are to be retrieved.

	Returns:
		list: A list of subscription tokens associated with the user.
	"""
	user_data = users.get_user_data(username)
	return [i['token'] for i in db.subscriptions.find({'creator': user_data['_id']})]


def get_subscription(auth: str) -> dict | None:
	"""
	Retrieve a notification subscription token from the database using the provided authentication key.

	Args:
		auth (str): The authentication key used to find the subscription.

	Returns:
		dict | None: The subscription token if found, otherwise None.
	"""
	subscription = db.subscriptions.find_one({'token.keys.auth': auth})
	return subscription['token'] if subscription is not None else None


def create_subscription(username: str, subscription_token: dict) -> None:
	"""
	Create a notification subscription for a user.

	Args:
		username (str): The username of the user.
		subscription_token (dict): A dictionary containing the subscription token details.
			Expected keys are:
				- 'endpoint' (str): The endpoint URL of the subscription.
				- 'expirationTime' (int or None): The expiration time of the subscription.
				- 'keys' (dict): A dictionary containing the keys for the subscription.
					Expected keys are:
						- 'p256dh' (str): The p256dh key.
						- 'auth' (str): The auth key.

	Raises:
		exceptions.InvalidSubscriptionToken: If the subscription token is invalid.
	"""
	user_data = users.get_user_data(username)

	try:
		db.subscriptions.insert_one({
			'creator': user_data['_id'],
			'token': {
				'endpoint': subscription_token['endpoint'],
				'expirationTime': subscription_token['expirationTime'],
				'keys': {
					'p256dh': subscription_token['keys']['p256dh'],
					'auth': subscription_token['keys']['auth'],
				},
			},
		})
	except TypeError | KeyError:
		raise exceptions.InvalidSubscriptionToken


def delete_subscriptions(username: str) -> int:
	"""
	Delete all notification subscription records for a given user.

	Args:
		username (str): The username of the user whose subscriptions are to be deleted.

	Returns:
		int: The number of subscription records that were deleted.
	"""
	user_data = users.get_user_data(username)
	return db.subscriptions.delete_many({'creator': user_data['_id']}).deleted_count


def delete_subscription(auth: str) -> int:
	"""
	Deletes all notification subscriptions from the database that match the given authentication token.

	Args:
		auth (str): The authentication token used to identify subscriptions to delete.

	Returns:
		int: The number of subscriptions deleted.
	"""
	return db.subscriptions.delete_many({'token.keys.auth': auth}).deleted_count


def mark_as_read(id: str) -> None:
	"""
	Marks a notification as read in the database.

	Args:
		id (str): The unique identifier of the notification to be marked as read.

	Returns:
		None
	"""
	db.notif_log.update_one({'_id': ObjectId(id)}, {'$set': {
		'read': True
	}})


def mark_all_as_read(username: str) -> None:
	"""
	Marks all notifications as read for a given user.

	Args:
		username (str): The username of the user whose notifications are to be marked as read.

	Returns:
		None
	"""
	user_data = users.get_user_data(username)
	db.notif_log.update_many({'recipient': user_data['_id'], 'read': False}, {'$set': {'read': True}})


def get_notifications(username: str, read: bool, start: int, count: int) -> list:
	"""
	Retrieve a list of notifications for a given user.

	Args:
		username (str): The username of the recipient.
		read (bool): Filter notifications based on their read status.
		start (int): The starting index for pagination.
		count (int): The number of notifications to retrieve.

	Returns:
		list: A list of notifications, each represented as a dictionary.
	"""
	user_data = users.get_user_data(username)
	selection = db.notif_log.find({'recipient': user_data['_id'], 'read': read}, sort=[('created', -1)])
	result = []
	for i in selection.limit(count).skip(start):
		i['id'] = str(i['_id'])
		result += [i]

	return result


def count_notifications(username: str, read: bool) -> int:
	"""
	Count the number of notifications for a given user based on their read status.

	Args:
		username (str): The username of the user whose notifications are to be counted.
		read (bool): The read status of the notifications to be counted (True for read, False for unread).

	Returns:
		int: The number of notifications that match the given criteria.
	"""
	user_data = users.get_user_data(username)
	return db.notif_log.count_documents({'recipient': user_data['_id'], 'read': read})


def send(title: str, body: str, username: str, *, category: str = 'general', read: bool = False) -> dict:
	"""
	Send a notification to a user and log the notification in the database.

	Args:
		title (str): The title of the notification.
		body (str): The body content of the notification.
		username (str): The username of the recipient.
		category (str, optional): The category of the notification. Defaults to 'general'.
		read (bool, optional): Whether the notification is marked as read. Defaults to False.

	Returns:
		dict: A dictionary containing the logged notification data.

	Raises:
		exceptions.MissingConfig: If the admin email configuration is missing.
	"""

	user_data = users.get_user_data(username)

	admin_email = settings.get_config('admin_email')

	if admin_email is None or admin_email == '':
		raise exceptions.MissingConfig('Admin Email')

	message = {
		'title': title,
		'body': body,
	}

	log_id = db.notif_log.insert_one({
		'recipient': user_data['_id'],
		'created': datetime.utcnow(),
		'message': json.dumps(message),
		'category': category,
		'device_count': 0,
		'read': read,
	}).inserted_id

	message['login_token'] = get_first_session_token(username)
	message['notif_id'] = str(log_id)

	sub_tokens = get_subscriptions(username)
	for subscription_token in sub_tokens:
		url = urlsplit(subscription_token['endpoint'])
		endpoint = f'{url.scheme}://{url.netloc}'

		try:
			webpush(
				subscription_info=subscription_token,
				data=json.dumps(message),
				vapid_private_key=VAPID_PRIVATE_KEY,
				vapid_claims={
					'sub': f'mailto:{admin_email}',
					'aud': endpoint,
				}
			)
		except WebPushException as e:
			send_admin_alert = True

			# If user subscription is expired, just delete the subscription and continue
			# There's nothing else we can do in that case.
			if e.response.status_code == 410:
				print(f'A notification subscription for user "{username}" has expired.', flush=True)
				delete_subscription(subscription_token.get('keys', {}).get('auth'))
				send_admin_alert = False

			# Send notification to admins if an unhandled WebPushException occurs!
			if send_admin_alert:
				for user in users.get_admins():
					db.notif_log.insert_one({
						'recipient': user['_id'],
						'created': datetime.utcnow(),
						'message': json.dumps({'title': 'WebPushException when sending notification', 'body': f'WebPushException when sending notification to {username}:\n\n{e}\n\nMSG:\n{message["body"]}'}),
						'device_count': 0,
						'read': False,
						'category': 'webpushexception',
					})

	db.notif_log.update_one({'_id': log_id}, {'$set': {
		'device_count': len(sub_tokens),
	}})

	notif_data = db.notif_log.find_one({'_id': log_id})
	notif_data['id'] = notif_data['_id']

	return notif_data
