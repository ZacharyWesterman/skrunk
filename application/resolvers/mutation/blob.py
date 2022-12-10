from application.db.blob import delete_blob
import application.db.perms as perms

@perms.require(['admin'])
def resolve_delete_blob(_, info, id: str) -> bool:
	return delete_blob(id)
