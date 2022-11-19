from ariadne import MutationType
from .users import resolve_create_user, resolve_delete_user
from .weather import resolve_create_weather_user, resolve_delete_weather_user

mutation = MutationType()

mutation.set_field('createUser', resolve_create_user)
mutation.set_field('deleteUser', resolve_delete_user)
mutation.set_field('createWeatherUser', resolve_create_weather_user)
mutation.set_field('deleteWeatherUser', resolve_delete_weather_user)
