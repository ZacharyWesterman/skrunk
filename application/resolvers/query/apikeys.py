"""application.resolvers.query.apikeys"""

from application.db.apikeys import get_api_keys
from application.db import perms
from . import query


@query.field('getAPIKeys')
@perms.require('admin')
def resolve_get_api_keys(_, info) -> list:
	return get_api_keys()
