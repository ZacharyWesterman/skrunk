"""application.types.apifailederror"""

from typing import TypedDict


class ApiFailedError(TypedDict):
	message: str
