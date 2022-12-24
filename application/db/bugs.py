from application.tokens import decode_user_token, get_request_token
import application.exceptions as exceptions
from . import users

from bson.objectid import ObjectId
from datetime import datetime
from typing import Optional

db = None

def report_bug(title: str, text: str) -> bool:
	global db
	try:
		username = decode_user_token(get_request_token()).get('username')
		user_data = users.get_user_data(username)
	except exceptions.UserDoesNotExistError:
		return False

	db.insert_one({
		'created': datetime.utcnow(),
		'creator': user_data['_id'],
		'title': title,
		'body': text,
		'convo': [],
		'resolved': False,
	})

	return True

def get_bug_report(id: str) -> dict:
	report = db.find_one({'_id': ObjectId(id)})
	report['id'] = report['_id']
	return report

def get_bug_reports(username: Optional[str], start: int, count: int, resolved: bool) -> list:
	global db
	reports = []
	if username is None:
		selection = db.find({'resolved': resolved}, sort=[('created', -1)])
	else:
		try:
			user_data = users.get_user_data(username)
			selection = db.find({'creator': user_data['_id'], 'resolved': resolved}, sort=[('created', -1)])
		except exceptions.UserDoesNotExistError:
			return []

	for i in selection.limit(count).skip(start):
		i['id'] = i['_id']
		try:
			user_data = users.get_user_by_id(i['creator'])
			i['creator'] = user_data['username']
		except exceptions.UserDoesNotExistError:
			i['creator'] = str(i['creator'])
		reports += [i]

	return reports

def count_bug_reports(username: Optional[str], resolved: bool) -> int:
	global db
	if username is None:
		return db.count_documents({'resolved': resolved})

	try:
		user_data = users.get_user_data(username)
	except exceptions.UserDoesNotExistError:
		return 0

	return db.count_documents({'creator': user_data['_id'], 'resolved': resolved})
