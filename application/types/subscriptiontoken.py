"""application.types.subscriptiontoken"""

from typing import TypedDict
from bson.objectid import ObjectId
from .subscriptiontokenkeys import SubscriptionTokenKeys


class SubscriptionToken(TypedDict):
	"""
	A WebPush subscription token for a user.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The URL endpoint for the subscription.
	endpoint: str
	## The expiration time of the token, or null if it doesn't expire.
	expirationTime: str | None
	## The keys used for the subscription.
	keys: SubscriptionTokenKeys
