from ariadne import MutationType
from .users import *
from .weather import *
from .sessions import resolve_revoke_user_sessions
from .blob import resolve_delete_blob, resolve_set_blob_tags
from .bugs import *
from .book import *
from .settings import resolve_set_module_enabled

mutation = MutationType()

mutation.set_field('createUser', resolve_create_user)
mutation.set_field('deleteUser', resolve_delete_user)
mutation.set_field('updateUserTheme', resolve_update_user_theme)
mutation.set_field('deleteUserTheme', resolve_delete_user_theme)
mutation.set_field('updateUserPerms', resolve_update_user_perms)
mutation.set_field('revokeSessions', resolve_revoke_user_sessions)
mutation.set_field('updateUserPassword', resolve_update_user_password)
mutation.set_field('updateUserDisplayName', resolve_update_user_display_name)

mutation.set_field('createWeatherUser', resolve_create_weather_user)
mutation.set_field('deleteWeatherUser', resolve_delete_weather_user)
mutation.set_field('enableWeatherUser', resolve_enable_weather_user)
mutation.set_field('disableWeatherUser', resolve_disable_weather_user)
mutation.set_field('updateWeatherUser', resolve_update_weather_user)

mutation.set_field('deleteBlob', resolve_delete_blob)
mutation.set_field('setBlobTags', resolve_set_blob_tags)

mutation.set_field('reportBug', resolve_report_bug)
mutation.set_field('deleteBug', resolve_delete_bug)
mutation.set_field('setBugStatus', resolve_set_bug_status)

mutation.set_field('linkBookTag', resolve_link_book_tag)
mutation.set_field('unlinkBookTag', resolve_unlink_book_tag)
mutation.set_field('shareBook', resolve_share_book_with_user)
mutation.set_field('shareBookNonUser', resolve_share_book_with_non_user)
mutation.set_field('borrowBook', resolve_borrow_book)
mutation.set_field('returnBook', resolve_return_book)

mutation.set_field('setModuleEnabled', resolve_set_module_enabled)