"""application.resolvers.query.settings"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.settings import (get_all_configs, get_all_themes,
                                     get_config, get_enabled_modules,
                                     get_groups, get_modules)
from application.integrations import graphql

from . import query


@query.field('getEnabledModules')
def resolve_get_enabled_modules(_, info: GraphQLResolveInfo) -> list:
	return get_enabled_modules(perms.caller_info_strict())


@query.field('getModules')
def resolve_get_modules(_, info: GraphQLResolveInfo) -> list:
	return get_modules(perms.caller_info_strict())


@query.field('getServerEnabledModules')
def resolve_get_server_enabled_modules(_, info: GraphQLResolveInfo, group: str | None) -> list:
	return get_enabled_modules(group=group)


@query.field('getUserGroups')
def resolve_get_groups(_, info: GraphQLResolveInfo) -> list:
	return get_groups()


@query.field('getConfigs')
@perms.require('admin')
def resolve_get_all_configs(_, info: GraphQLResolveInfo) -> dict:
	return {'__typename': 'ConfigList', 'configs': get_all_configs()}


@query.field('getConfig')
def resolve_get_config(_, info: GraphQLResolveInfo, name: str) -> str | None:
	return get_config(name)


@query.field('getThemes')
@perms.module('theme')
def resolve_get_themes(_, info: GraphQLResolveInfo) -> list:
	return get_all_themes()


@query.field('getSchema')
def resolve_get_schema(_, info: GraphQLResolveInfo) -> dict:
	return graphql.schema()
