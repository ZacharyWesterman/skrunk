from application.db.apikeys import new_api_key, delete_api_key
from application.db import perms

@perms.require(['admin'])
def resolve_create_api_key(_, info, description: str) -> str:
	return new_api_key(description)

@perms.require(['admin'])
def resolve_delete_api_key(_, info, key: str) -> bool:
	return delete_api_key(key)
