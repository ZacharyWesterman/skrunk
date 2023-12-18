from flask import request, Response, jsonify
from pywebpush import webpush, WebPushException
import os, json

VAPID_CLAIMS = {
	"sub": "mailto:westerman.zachary@gmail.com",
	# "aud": "https://ftp.skrunky.com",
}

DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH = os.path.join(os.getcwd(),'data/private_key.txt')
DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH = os.path.join(os.getcwd(),'data/public_key.txt')

VAPID_PRIVATE_KEY = open(DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH, 'r+').readline().strip('\n')
VAPID_PUBLIC_KEY = open(DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH, 'r+').read().strip('\n')

PUSH_SUBSCRIPTION = None

def subscription() -> Response:
	global VAPID_PUBLIC_KEY
	global PUSH_SUBSCRIPTION

	if request.method == 'GET':
		return Response(
			response = VAPID_PUBLIC_KEY,
			headers = {'Access-Control-Allow-Origin': '*'},
			content_type = 'text/plain'
		)

	subscription_token = request.get_json()
	PUSH_SUBSCRIPTION = subscription_token

	return Response('Subscription successful.')

def push() -> Response:
	global VAPID_CLAIMS
	global VAPID_PRIVATE_KEY
	global PUSH_SUBSCRIPTION

	message = 'Test push notification'

	try:
		notif = webpush(
			subscription_info=PUSH_SUBSCRIPTION,
			data=message,
			vapid_private_key=VAPID_PRIVATE_KEY,
			vapid_claims=VAPID_CLAIMS
		)
		print(notif, flush=True)

	except WebPushException as e:
		print(f'WebPushException: {e}', flush=True)

	return Response('Sent push notification.')