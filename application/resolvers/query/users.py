import application.exceptions as exceptions
from application.db.users import get_user_data, get_user_list
import application.db.perms as perms

def resolve_get_user(_, info, username: str) -> dict:
	try:
		return { '__typename': 'UserData', **get_user_data(username) }
	except exceptions.ClientError as e:
		return { '__typename': 'UserDoesNotExistError', 'message': str(e) }

def resolve_list_users(_, info, restrict: bool) -> list:
	user_data = perms.caller_info(info)
	if not restrict and perms.user_has_perms(user_data, ['admin']):
		return get_user_list()
	else:
		return get_user_list(user_data.get('groups', []))
