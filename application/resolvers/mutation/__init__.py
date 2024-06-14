from ariadne import MutationType
from .users import *
from .weather import *
from .sessions import resolve_revoke_user_sessions
from .blob import *
from .bugs import *
from .book import *
from .settings import resolve_set_module_enabled, resolve_set_config_value, resolve_create_theme, resolve_delete_theme
from .notification import *
from .apikeys import resolve_create_api_key, resolve_delete_api_key
from .inventory import resolve_create_inventory_item

mutation = MutationType()

mutation.set_field('createUser', resolve_create_user)
mutation.set_field('deleteUser', resolve_delete_user)
mutation.set_field('updateUserTheme', resolve_update_user_theme)
mutation.set_field('deleteUserTheme', resolve_delete_user_theme)
mutation.set_field('updateUserPerms', resolve_update_user_perms)
mutation.set_field('revokeSessions', resolve_revoke_user_sessions)
mutation.set_field('updateUserPassword', resolve_update_user_password)
mutation.set_field('updateUserDisplayName', resolve_update_user_display_name)
mutation.set_field('updateUserGroups', resolve_set_user_groups)
mutation.set_field('updateUserModule', resolve_set_user_module)
mutation.set_field('updateUserEmail', resolve_update_user_email)


mutation.set_field('createWeatherUser', resolve_create_weather_user)
mutation.set_field('deleteWeatherUser', resolve_delete_weather_user)
mutation.set_field('enableWeatherUser', resolve_enable_weather_user)
mutation.set_field('disableWeatherUser', resolve_disable_weather_user)
mutation.set_field('updateWeatherUser', resolve_update_weather_user)

mutation.set_field('deleteBlob', resolve_delete_blob)
mutation.set_field('setBlobTags', resolve_set_blob_tags)
mutation.set_field('createZipArchive', resolve_create_zip_archive)
mutation.set_field('getBlobFromQR', resolve_generate_blob_from_qr)
mutation.set_field('setBlobHidden', resolve_set_blob_hidden)
mutation.set_field('setBlobEphemeral', resolve_set_blob_ephemeral)

mutation.set_field('reportBug', resolve_report_bug)
mutation.set_field('deleteBug', resolve_delete_bug)
mutation.set_field('setBugStatus', resolve_set_bug_status)
mutation.set_field('commentOnBug', resolve_comment_on_bug)

mutation.set_field('linkBookTag', resolve_link_book_tag)
mutation.set_field('unlinkBookTag', resolve_unlink_book_tag)
mutation.set_field('shareBook', resolve_share_book_with_user)
mutation.set_field('shareBookNonUser', resolve_share_book_with_non_user)
mutation.set_field('borrowBook', resolve_borrow_book)
mutation.set_field('requestToBorrowBook', resolve_request_borrow_book)
mutation.set_field('returnBook', resolve_return_book)
mutation.set_field('setBookOwner', resolve_change_book_owner)
mutation.set_field('editBook', resolve_edit_book)
mutation.set_field('createBook', resolve_create_book)
mutation.set_field('appendEBook', resolve_append_ebook)

mutation.set_field('setModuleEnabled', resolve_set_module_enabled)
mutation.set_field('setConfig', resolve_set_config_value)
mutation.set_field('createTheme', resolve_create_theme)
mutation.set_field('deleteTheme', resolve_delete_theme)

mutation.set_field('createSubscription', resolve_create_subscription)
mutation.set_field('deleteSubscription', resolve_delete_subscription)
mutation.set_field('deleteSubscriptions', resolve_delete_subscriptions)
mutation.set_field('sendNotification', resolve_send_notification)
mutation.set_field('markNotifAsRead', resolve_mark_notification_as_read)
mutation.set_field('markAllNotifsAsRead', resolve_mark_all_notifications_as_read)

mutation.set_field('createAPIKey', resolve_create_api_key)
mutation.set_field('deleteAPIKey', resolve_delete_api_key)

mutation.set_field('createInventoryItem', resolve_create_inventory_item)
