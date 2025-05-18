from typing import TypedDict
from .config import Config


class ConfigList(TypedDict):
	configs: list[Config | None]
