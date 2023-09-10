from application.db.settings import get_enabled_modules, get_groups

def resolve_get_enabled_modules(_, info) -> list:
    return get_enabled_modules()

def resolve_get_groups(_, info) -> list:
    return get_groups()