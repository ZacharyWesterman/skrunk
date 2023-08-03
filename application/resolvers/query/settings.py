from application.db.settings import get_enabled_modules
import application.db.perms as perms

@perms.require(['admin'])
def resolve_get_enabled_modules(_, info) -> list:
    return get_enabled_modules()