from application.db.settings import get_enabled_modules, get_groups, get_all_configs

def resolve_get_enabled_modules(_, info) -> list:
    return get_enabled_modules()

def resolve_get_groups(_, info) -> list:
    return get_groups()

def resolve_get_all_configs(_, info) -> list:
    return get_all_configs()