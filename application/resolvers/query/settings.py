from application.db.settings import get_enabled_modules, get_groups, get_all_configs, get_config, get_modules, get_all_themes
from application.db import perms

def resolve_get_enabled_modules(_, info) -> list:
    return get_enabled_modules(perms.caller_info())

def resolve_get_modules(_, info) -> list:
    return get_modules(perms.caller_info())

def resolve_get_server_enabled_modules(_, info, group: str|None) -> list:
    return get_enabled_modules(group = group)

def resolve_get_groups(_, info) -> list:
    return get_groups()

@perms.require(['admin'])
def resolve_get_all_configs(_, info) -> list:
    return { '__typename': 'ConfigList', 'configs': get_all_configs() }

def resolve_get_config(_, info, name: str) -> str|None:
    return get_config(name)

def resolve_get_themes(_, info) -> list:
    return get_all_themes()
