from ariadne import QueryType
from .users import resolve_get_user, resolve_list_users
from .weather import resolve_get_weather_users, resolve_get_last_execution, resolve_get_alert_history
from .sessions import resolve_count_user_sessions
from .blob import *
from .bugs import *
from .book import *
from .settings import *
from .integrations import resolve_search_subsonic
from .integrations import resolve_get_system_info
from .notification import *
from .apikeys import resolve_get_api_keys
from .inventory import *
from .datafeed import *

query = QueryType()

query.set_field('getUser', resolve_get_user)
query.set_field('listUsers', resolve_list_users)
query.set_field('countSessions', resolve_count_user_sessions)

query.set_field('getWeatherUsers', resolve_get_weather_users)
query.set_field('getLastWeatherExec', resolve_get_last_execution)
query.set_field('weatherAlertHistory', resolve_get_alert_history)

query.set_field('getBlobs', resolve_get_blobs)
query.set_field('countBlobs', resolve_count_blobs)
query.set_field('getBlob', resolve_get_blob)
query.set_field('totalBlobSize', resolve_total_blob_size)
query.set_field('getQRFromBlob', resolve_process_qr_from_blob)
query.set_field('countTagUses', resolve_count_tag_uses)
query.set_field('generateUID', resolve_generate_uid)
query.set_field('pollZipProgress', resolve_poll_zip_progress)

query.set_field('getBugReports', resolve_get_bug_reports)
query.set_field('countBugReports', resolve_count_bug_reports)
query.set_field('getBugReport', resolve_get_bug_report)
query.set_field('getOpenIssues', resolve_get_issues)
query.set_field('getPendingIssues', resolve_get_pending_issues)

query.set_field('getBooks', resolve_get_books)
query.set_field('countBooks', resolve_count_books)
query.set_field('searchBooks', resolve_search_google_books)
query.set_field('getBookByTag', resolve_get_book_by_tag)
query.set_field('countAllUserBooks', resolve_count_all_user_books)

query.set_field('getEnabledModules', resolve_get_enabled_modules)
query.set_field('getModules', resolve_get_modules)
query.set_field('getServerEnabledModules', resolve_get_server_enabled_modules)
query.set_field('getUserGroups', resolve_get_groups)
query.set_field('getConfigs', resolve_get_all_configs)
query.set_field('getConfig', resolve_get_config)
query.set_field('getThemes', resolve_get_themes)
query.set_field('getSchema', resolve_get_schema)

query.set_field('searchSubsonic', resolve_search_subsonic)
query.set_field('getSystemInfo', resolve_get_system_info)

query.set_field('getVAPIDPublicKey', resolve_get_vapid_public_key)
query.set_field('getSubscription', resolve_get_subscription)
query.set_field('getSubscriptions', resolve_get_subscriptions)
query.set_field('getNotifications', resolve_get_notifications)
query.set_field('countNotifications', resolve_count_notifications)

query.set_field('getAPIKeys', resolve_get_api_keys)

query.set_field('getItemCategories', resolve_get_item_categories)
query.set_field('getItemTypes', resolve_get_item_types)
query.set_field('getItemLocations', resolve_get_item_locations)
query.set_field('getInventory', resolve_get_inventory)
query.set_field('countInventory', resolve_count_inventory)

query.set_field('getUserFeeds', resolve_get_user_feeds)
query.set_field('getFeedDocuments', resolve_get_feed_documents)
query.set_field('countFeedDocuments', resolve_count_feed_documents)
query.set_field('getFeed', resolve_get_feed)
query.set_field('getFeeds', resolve_get_feeds)
query.set_field('countFeeds', resolve_count_feeds)
