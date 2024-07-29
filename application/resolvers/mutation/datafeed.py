from application.db.datafeed import create_feed, delete_feed, get_feed, set_feed_notify
from ..decorators import *
from application.db import perms

@perms.module('feed')
@handle_client_exceptions
def resolve_create_feed(_, info, name: str, url: str, kind: str, notify: bool) -> dict:
	return { '__typename': 'Feed', **create_feed(name, url, kind, notify) }

@perms.module('feed')
@handle_client_exceptions
@perms.require('admin', perform_on_self = True, data_func = get_feed)
def resolve_delete_feed(_, info, id: str) -> dict:
	return { '__typename': 'Feed', **delete_feed(id) }

@perms.module('feed')
@perms.require('admin', perform_on_self = True, data_func = get_feed)
@handle_client_exceptions
def resolve_update_feed_notify(_, info, id: str, notify: bool) -> dict:
	return { '__typename': 'Feed', **set_feed_notify(id, notify) }
