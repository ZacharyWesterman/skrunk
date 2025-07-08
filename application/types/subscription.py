"""application.types.subscription"""

from typing import TypedDict
from .subscriptionkeys import SubscriptionKeys


class Subscription(TypedDict):
	"""
	A WebPush subscription for a user.
	"""

	## The URL endpoint for the subscription.
	endpoint: str
	## The expiration time of the token, or null if it doesn't expire.
	expirationTime: str | None
	## The keys used for the subscription.
	keys: SubscriptionKeys
