"""application.types.subscriptiontokenkeys"""

from typing import TypedDict
from bson.objectid import ObjectId


class SubscriptionTokenKeys(TypedDict):
	"""
	A pair of keys used for a WebPush subscription token.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The public key used for encryption.
	p256dh: str
	## The authentication secret used for the subscription.
	auth: str
