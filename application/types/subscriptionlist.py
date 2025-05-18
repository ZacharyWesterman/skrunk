from typing import TypedDict
from .subscription import Subscription

class SubscriptionList(TypedDict):
	list: list[Subscription | None]

