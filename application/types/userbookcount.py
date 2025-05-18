from typing import TypedDict
from .usermindata import UserMinData

class UserBookCount(TypedDict):
	owner: UserMinData | None
	count: int

