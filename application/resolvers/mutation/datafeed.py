from application.db.datafeed import create_feed, delete_feed
from ..decorators import *
from application.db import perms

@perms.module('feed')
@handle_client_exceptions
def resolve_create_feed(_, info, name: str, url: str, kind: str, notify: bool) -> dict:
	return { '__typename': 'Feed', **create_feed(name, url, kind, notify) }

@perms.module('feed')
@handle_client_exceptions
def resolve_delete_feed(_, info, id: str) -> dict:
	return { '__typename': 'Feed', **delete_feed(id) }
