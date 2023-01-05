from ariadne import MutationType
from .users import *
from .weather import *
from .sessions import resolve_revoke_user_sessions
from .blob import resolve_delete_blob, resolve_set_blob_tags
from .bugs import resolve_report_bug, resolve_delete_bug

mutation = MutationType()

mutation.set_field('createUser', resolve_create_user)
mutation.set_field('deleteUser', resolve_delete_user)
mutation.set_field('updateUserTheme', resolve_update_user_theme)
mutation.set_field('updateUserPerms', resolve_update_user_perms)
mutation.set_field('revokeSessions', resolve_revoke_user_sessions)
mutation.set_field('updateUserPassword', resolve_update_user_password)

mutation.set_field('createWeatherUser', resolve_create_weather_user)
mutation.set_field('deleteWeatherUser', resolve_delete_weather_user)
mutation.set_field('enableWeatherUser', resolve_enable_weather_user)
mutation.set_field('disableWeatherUser', resolve_disable_weather_user)
mutation.set_field('updateWeatherUser', resolve_update_weather_user)

mutation.set_field('deleteBlob', resolve_delete_blob)
mutation.set_field('setBlobTags', resolve_set_blob_tags)

mutation.set_field('reportBug', resolve_report_bug)
mutation.set_field('deleteBug', resolve_delete_bug)
