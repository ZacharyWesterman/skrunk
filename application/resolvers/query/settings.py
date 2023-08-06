from application.db.settings import get_enabled_modules

def resolve_get_enabled_modules(_, info) -> list:
    return get_enabled_modules()