from application.db.datafeed import create_feed
from application.exceptions import ClientError

from ..decorators import handle_client_exceptions

@handle_client_exceptions
def resolve_create_feed(_, info, name: str, url: str, kind: str, notify: bool) -> dict:
	return { '__typename': 'Feed', **create_feed(name, url, kind, notify)}
