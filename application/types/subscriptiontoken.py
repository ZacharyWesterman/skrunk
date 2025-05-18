from typing import TypedDict
from .subscriptiontokenkeys import SubscriptionTokenKeys

class SubscriptionToken(TypedDict):
	endpoint: str
	expirationTime: str
	keys: SubscriptionTokenKeys | None

