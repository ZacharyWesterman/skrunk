from application.db import settings, users
from application import exceptions
from pywebpush import webpush, WebPushException
from urllib.parse import urlsplit
from datetime import datetime

VAPID_PRIVATE_KEY = open('data/private_key.txt', 'r+').readline().strip('\n')
VAPID_PUBLIC_KEY = open('data/public_key.txt', 'r+').read().strip('\n')

db = None

def get_public_key() -> str:
	global VAPID_PUBLIC_KEY
	return VAPID_PUBLIC_KEY

def get_subscriptions(username: str) -> list:
	user_data = users.get_user_data(username)
	return [i['token'] for i in db.subscriptions.find({'creator': user_data['_id']})]

def get_subscription(p256dh: str) -> dict|None:
	subscription = db.subscriptions.find_one({'token.keys.p256dh': p256dh})
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

def delete_subscription(p256dh: str) -> int:
	return db.subscriptions.delete_many({'token.keys.p256dh': p256dh}).deleted_count

#May raise exceptions.WebPushException, exceptions.UserDoesNotExistError, or exceptions.MissingConfig
def send(message: str, username: str, *, category: str = 'general') -> None:
	global VAPID_PRIVATE_KEY

	user_data = users.get_user_data(username)

	admin_email = settings.get_config('admin_email')

	if admin_email is None or admin_email == '':
		raise exceptions.MissingConfig('Admin Email')

	sub_tokens = get_subscriptions(username)
	for subscription_token in sub_tokens:
		url = urlsplit(subscription_token['endpoint'])
		endpoint = f'{url.scheme}://{url.netloc}'

		try:
			webpush(
				subscription_info = subscription_token,
				data = message,
				vapid_private_key = VAPID_PRIVATE_KEY,
				vapid_claims = {
					'sub': f'mailto:{admin_email}',
					'aud': endpoint,
				}
			)
		except WebPushException as e:
			raise exceptions.WebPushException(str(e))

	db.log.insert_one({
		'recipient': user_data['_id'],
		'created': datetime.utcnow(),
		'message': message,
		'category': category,
		'device_count': len(sub_tokens),
	})
