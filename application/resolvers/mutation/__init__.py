from ariadne import MutationType
from .users import *
from .weather import *

mutation = MutationType()

mutation.set_field('createUser', resolve_create_user)
mutation.set_field('deleteUser', resolve_delete_user)
mutation.set_field('updateUserTheme', resolve_update_user_theme)
mutation.set_field('updateUserCreds', resolve_update_user_creds)

mutation.set_field('createWeatherUser', resolve_create_weather_user)
mutation.set_field('deleteWeatherUser', resolve_delete_weather_user)
mutation.set_field('enableWeatherUser', resolve_enable_weather_user)
mutation.set_field('disableWeatherUser', resolve_disable_weather_user)
mutation.set_field('updateWeatherUser', resolve_update_weather_user)
