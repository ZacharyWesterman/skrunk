from ariadne import MutationType
from .users import resolve_authenticate

mutation = MutationType()

mutation.set_field('authenticate', resolve_authenticate)
