from application.db.settings import set_module_enabled, get_enabled_modules, set_config
import application.db.perms as perms

@perms.require(['admin'])
def resolve_set_module_enabled(_, info, module_id: str, enabled: bool) -> list:
    set_module_enabled(module_id, enabled)
    return get_enabled_modules()

@perms.require(['admin'])
def resolve_set_config_value(_, info, name: str, value: str|None) -> bool:
    set_config(name, value)
    return True