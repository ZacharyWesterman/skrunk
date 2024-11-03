from application.db.settings import get_enabled_modules, get_groups, get_all_configs, get_config, get_modules, get_all_themes
from application.db import perms
from application.integrations import graphql
from . import query

@query.field('getEnabledModules')
def resolve_get_enabled_modules(_, info) -> list:
    return get_enabled_modules(perms.caller_info())

@query.field('getModules')
def resolve_get_modules(_, info) -> list:
    return get_modules(perms.caller_info())

@query.field('getServerEnabledModules')
def resolve_get_server_enabled_modules(_, info, group: str|None) -> list:
    return get_enabled_modules(group = group)

@query.field('getUserGroups')
def resolve_get_groups(_, info) -> list:
    return get_groups()

@query.field('getConfigs')
@perms.require('admin')
def resolve_get_all_configs(_, info) -> list:
    return { '__typename': 'ConfigList', 'configs': get_all_configs() }

@query.field('getConfig')
def resolve_get_config(_, info, name: str) -> str|None:
    return get_config(name)

@query.field('getThemes')
@perms.module('theme')
def resolve_get_themes(_, info) -> list:
    return get_all_themes()

@query.field('getSchema')
def resolve_get_schema(_, info) -> dict:
    return graphql.schema()
