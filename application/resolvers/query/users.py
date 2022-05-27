def resolve_get_user(_, info, username: str) -> dict:
	return {'__typename': 'UserData', 'username':username}
