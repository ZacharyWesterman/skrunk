from application.db import settings, users
from application.db.sessions import get_first_session_token
from application import exceptions
from pywebpush import webpush, WebPushException
from urllib.parse import urlsplit
from datetime import datetime
from bson.objectid import ObjectId
import json

try:
	VAPID_PRIVATE_KEY = open('data/private_key.txt', 'r+').readline().strip('\n')
	VAPID_PUBLIC_KEY = open('data/public_key.txt', 'r+').read().strip('\n')
except FileNotFoundError:
	print('WARNING: No VAPID keys found!', flush=True)
	pass

from pymongo.database import Database
db: Database = None


def get_user_from_notif(id: str) -> dict:
	notif = db.notif_log.find_one({'_id': ObjectId(id)})
	if notif is None:
		return {}

	return users.get_user_by_id(notif.get('recipient'))


def get_public_key() -> str:
	return VAPID_PUBLIC_KEY


def get_subscriptions(username: str) -> list:
	user_data = users.get_user_data(username)
	return [i['token'] for i in db.subscriptions.find({'creator': user_data['_id']})]


def get_subscription(auth: str) -> dict | None:
	subscription = db.subscriptions.find_one({'token.keys.auth': auth})
	return subscription['token'] if subscription is not None else None


def create_subscription(username: str, subscription_token: dict) -> None:
	global db
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
	except TypeError:
		raise exceptions.InvalidSubscriptionToken
	except KeyError:
		raise exceptions.InvalidSubscriptionToken


def delete_subscriptions(username: str) -> int:
	user_data = users.get_user_data(username)
	return db.subscriptions.delete_many({'creator': user_data['_id']}).deleted_count


def delete_subscription(auth: str) -> int:
	return db.subscriptions.delete_many({'token.keys.auth': auth}).deleted_count


def mark_as_read(id: str) -> None:
	db.notif_log.update_one({'_id': ObjectId(id)}, {'$set': {
		'read': True
	}})


def mark_all_as_read(username: str) -> None:
	user_data = users.get_user_data(username)
	db.notif_log.update_many({'recipient': user_data['_id'], 'read': False}, {'$set': {'read': True}})


def get_notifications(username: str, read: bool, start: int, count: int) -> list:
	user_data = users.get_user_data(username)
	selection = db.notif_log.find({'recipient': user_data['_id'], 'read': read}, sort=[('created', -1)])
	result = []
	for i in selection.limit(count).skip(start):
		i['id'] = str(i['_id'])
		result += [i]

	return result


def count_notifications(username: str, read: bool) -> int:
	user_data = users.get_user_data(username)
	return db.notif_log.count_documents({'recipient': user_data['_id'], 'read': read})

# May raise exceptions.WebPushException, exceptions.UserDoesNotExistError, or exceptions.MissingConfig


def send(title: str, body: str, username: str, *, category: str = 'general', read: bool = False) -> dict:
	global VAPID_PRIVATE_KEY

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
