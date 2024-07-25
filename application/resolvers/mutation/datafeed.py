from application.db.datafeed import create_feed, delete_feed
from ..decorators import *

@handle_client_exceptions
def resolve_create_feed(_, info, name: str, url: str, kind: str, notify: bool) -> dict:
	return { '__typename': 'Feed', **create_feed(name, url, kind, notify) }

@handle_client_exceptions
def resolve_delete_feed(_, info, id: str) -> dict:
	return { '__typename': 'Feed', **delete_feed(id) }
