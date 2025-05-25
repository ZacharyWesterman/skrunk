from typing import TypedDict
from .diskusage import DiskUsage


class SystemInfo(TypedDict):
	storage: list[DiskUsage]
