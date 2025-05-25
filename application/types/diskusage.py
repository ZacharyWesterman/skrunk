"""application.types.diskusage"""

from typing import TypedDict


class DiskUsage(TypedDict):
	name: str
	total: float
	free: float
	used: float
