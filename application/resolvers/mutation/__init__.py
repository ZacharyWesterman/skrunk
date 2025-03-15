"""application.resolvers.mutation"""

from ariadne import MutationType

## The MutationType object for the GraphQL schema.
mutation = MutationType()

from . import apikeys  # nopep8
from . import users  # nopep8
from . import weather  # nopep8
from . import sessions  # nopep8
from . import blob  # nopep8
from . import bugs  # nopep8
from . import book  # nopep8
from . import settings  # nopep8
from . import notification  # nopep8
from . import inventory  # nopep8
from . import datafeed  # nopep8
from . import documents  # nopep8
