"""application.types.subscriptionlist"""

from typing import TypedDict
from .subscription import Subscription


class SubscriptionList(TypedDict):
	"""
	A list of WebPush subscriptions for a user.
	"""

	## The list of subscriptions.
	list: list[Subscription]
