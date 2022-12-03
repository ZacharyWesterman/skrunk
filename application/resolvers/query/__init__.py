from ariadne import QueryType
from .users import resolve_get_user, resolve_list_users
from .weather import resolve_get_weather_users, resolve_get_last_execution

query = QueryType()

query.set_field('getUser', resolve_get_user)
query.set_field('listUsers', resolve_list_users)
query.set_field('getWeatherUsers', resolve_get_weather_users)
query.set_field('getLastWeatherExec', resolve_get_last_execution)
