from application.tokens import decode_user_token, get_request_token
import application.exceptions as exceptions
from . import users

from bson.objectid import ObjectId
from datetime import datetime
import markdown, html

db = None

def report_bug(text: str, plaintext: bool = True) -> dict:
	global db
	username = decode_user_token(get_request_token()).get('username')
	user_data = users.get_user_data(username)

	id = db.insert_one({
		'created': datetime.utcnow(),
		'creator': user_data['_id'],
		'body': text,
		'body_html': html.escape(text) if plaintext else markdown.markdown(text, output_format = 'html'),
		'convo': [],
		'resolved': False,
	}).inserted_id

	bug_report = db.find_one({'_id': id})
	bug_report['id'] = bug_report['_id']
	return bug_report

def comment_on_bug(id: str, text: str, plaintext: bool = True) -> dict:
	username = decode_user_token(get_request_token()).get('username')
	user_data = users.get_user_data(username)

	report = db.find_one({'_id': ObjectId(id)})
	if report is None:
		raise exceptions.BugReportDoesNotExistError(id)

	convo_data = {
		'created': datetime.utcnow(),
		'creator': user_data['_id'],
		'body': text,
		'body_html': html.escape(text) if plaintext else markdown.markdown(text, output_format = 'html'),
	}

	db.update_one({'_id': ObjectId(id)}, {
		'$push': {'convo': convo_data }
	})

	report['convo'] += [convo_data]
	return process_bug_report(report)

def process_bug_report(report: dict) -> dict:
	report['id'] = report['_id']

	try:
		user_data = users.get_user_by_id(report['creator'])
		report['creator'] = user_data['username']
	except exceptions.UserDoesNotExistError:
		report['creator'] = str(report['creator'])

	processed_comments = []
	for comment in report['convo']:
		try:
			user_data = users.get_user_by_id(comment['creator'])
			comment['creator'] = user_data['username']
		except exceptions.UserDoesNotExistError:
			comment['creator'] = str(comment['creator'])

		processed_comments += [comment]

	report['convo'] = processed_comments
	return report

def get_bug_report(id: str) -> dict:
	report = db.find_one({'_id': ObjectId(id)})
	if report is None:
		raise exceptions.BugReportDoesNotExistError(id)

	return process_bug_report(report)

def get_bug_reports(username: str|None, start: int, count: int, resolved: bool) -> list:
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
		reports += [process_bug_report(i)]

	return reports

def count_bug_reports(username: str|None, resolved: bool) -> int:
	global db
	if username is None:
		return db.count_documents({'resolved': resolved})

	try:
		user_data = users.get_user_data(username)
	except exceptions.UserDoesNotExistError:
		return 0

	return db.count_documents({'creator': user_data['_id'], 'resolved': resolved})

def delete_bug_report(id: str) -> dict:
	global db
	bug_report = db.find_one({'_id': ObjectId(id)})
	if bug_report is None:
		raise exceptions.BugReportDoesNotExistError(id)

	db.delete_one({'_id': ObjectId(id)})
	bug_report['id'] = bug_report['_id']
	return bug_report

def set_bug_status(id: str, status: bool) -> dict:
	global db
	bug_report = db.find_one({'_id': ObjectId(id)})
	if bug_report is None:
		raise exceptions.BugReportDoesNotExistError(id)

	db.update_one({'_id': ObjectId(id)}, {'$set':{'resolved': status}})
	bug_report['resolved'] = status
	return bug_report