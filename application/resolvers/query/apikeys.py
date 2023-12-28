from application.db.apikeys import get_api_keys
from application.db import perms

@perms.require(['admin'])
def resolve_get_api_keys(_, info) -> list:
	return get_api_keys()
