"""application.types.subscriptionkeys"""

from typing import TypedDict


class SubscriptionKeys(TypedDict):
	"""
	A pair of keys used for a WebPush subscription.
	"""

	## The public key used for encryption.
	p256dh: str
	## The authentication secret used for the subscription.
	auth: str
