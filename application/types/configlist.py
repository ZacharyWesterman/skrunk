"""application.types.configlist"""

from typing import TypedDict
from .config import Config


class ConfigList(TypedDict):
	"""
	A list of configuration settings.
	"""

	## The list of configuration settings.
	configs: list[Config]
