from application.db.settings import set_module_enabled, get_enabled_modules
import application.db.perms as perms

@perms.require(['admin'])
def resolve_set_module_enabled(_, info, module_id: str, enabled: bool) -> list:
    set_module_enabled(module_id, enabled)
    return get_enabled_modules()
