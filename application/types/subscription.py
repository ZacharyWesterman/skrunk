"""application.types.subscription"""

from typing import TypedDict
from .subscriptionkeys import SubscriptionKeys


class Subscription(TypedDict):
	endpoint: str
	expirationTime: str
	keys: SubscriptionKeys
