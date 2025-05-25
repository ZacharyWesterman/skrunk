"""application.types.subscriptiontokenkeys"""

from typing import TypedDict


class SubscriptionTokenKeys(TypedDict):
	"""
	A pair of keys used for a WebPush subscription token.
	"""

	## The public key used for encryption.
	p256dh: str
	## The authentication secret used for the subscription.
	auth: str
