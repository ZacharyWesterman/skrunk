"""application.types.subscriptionlist"""

from typing import TypedDict
from bson.objectid import ObjectId
from .subscription import Subscription


class SubscriptionList(TypedDict):
	"""
	A list of WebPush subscriptions for a user.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The list of subscriptions.
	list: list[Subscription]
