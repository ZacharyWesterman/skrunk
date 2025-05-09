"""application.resolvers.query"""

from ariadne import QueryType

## The QueryType object for the GraphQL schema.
query = QueryType()

from . import apikeys  # nopep8
from . import users  # nopep8
from . import weather  # nopep8
from . import sessions  # nopep8
from . import blob  # nopep8
from . import bugs  # nopep8
from . import book  # nopep8
from . import settings  # nopep8
from . import integrations  # nopep8
from . import integrations  # nopep8
from . import notification  # nopep8
from . import inventory  # nopep8
from . import datafeed  # nopep8
from . import last_mutation  # nopep8
