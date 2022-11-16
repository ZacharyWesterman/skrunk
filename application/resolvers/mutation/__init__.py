from ariadne import MutationType
from .users import resolve_create_user

mutation = MutationType()

mutation.set_field('createUser', resolve_create_user)
