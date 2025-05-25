"""application.types.systeminfo"""

from typing import TypedDict
from .diskusage import DiskUsage


class SystemInfo(TypedDict):
	"""
	System information about the server.
	"""

	## A list usage statistics for each discrete disk on the server.
	storage: list[DiskUsage]
