from ariadne import QueryType
from .users import resolve_get_user, resolve_list_users
from .weather import resolve_get_weather_users, resolve_get_last_execution
from .sessions import resolve_count_user_sessions
from .blob import *
from .bugs import *
from .book import resolve_search_books, resolve_get_book_by_tag

query = QueryType()

query.set_field('getUser', resolve_get_user)
query.set_field('listUsers', resolve_list_users)
query.set_field('countSessions', resolve_count_user_sessions)

query.set_field('getWeatherUsers', resolve_get_weather_users)
query.set_field('getLastWeatherExec', resolve_get_last_execution)

query.set_field('getBlobs', resolve_get_blobs)
query.set_field('countBlobs', resolve_count_blobs)
query.set_field('getBlob', resolve_get_blob)

query.set_field('getBugReports', resolve_get_bug_reports)
query.set_field('countBugReports', resolve_count_bug_reports)
query.set_field('getBugReport', resolve_get_bug_report)

query.set_field('searchBooks', resolve_search_books)
query.set_field('getBookByTag', resolve_get_book_by_tag)
