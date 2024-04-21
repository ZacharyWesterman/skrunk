from application.tokens import decode_user_token, get_request_token
import application.exceptions as exceptions
from . import users, notification

from bson.objectid import ObjectId
from datetime import datetime
import markdown, html

from pymongo.collection import Collection
db: Collection = None

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

	#Let all involved users know that the bug report has a new comment!
	for i in list(set([ i['creator'] for i in report['convo'] ])):
		#Don't send a notification if the user commented on their own bug report
		if i == user_data['_id']:
			continue

		this_user = users.get_user_by_id(i)
		whose = 'your' if i == report['creator'] else (this_user['display_name'] + "'s")

		notification.send(
			title = f'{user_data["display_name"]} commented on {whose} bug report',
			body = text[0:100],
			username = this_user['username'],
			category = 'bugs'
		)


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

def get_bug_reports(userids: list, start: int, count: int, resolved: bool) -> list:
	reports = []
	if len(userids) == 0:
		selection = db.find({'resolved': resolved}, sort=[('created', -1)])
	else:
		selection = db.find({
			'resolved': resolved,
			'$or': [ {'creator': i} for i in userids ],
		}, sort = [('created', -1)])

	for i in selection.limit(count).skip(start):
		reports += [process_bug_report(i)]

	return reports

def count_bug_reports(userids: list, resolved: bool) -> int:
	if len(userids) == 0:
		return db.count_documents({'resolved': resolved})
	else:
		return db.count_documents({
			'resolved': resolved,
			'$or': [ {'creator': i} for i in userids ],
		})

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

	username = decode_user_token(get_request_token()).get('username')
	user_data = users.get_user_data(username)

	send_user = users.get_user_by_id(bug_report['creator'])

	notification.send(
		title = f'A bug has been {"resolved" if status else "reopened"}',
		body = f'{user_data["display_name"]} has {"resolved" if status else "reopened"} the issue you reported:\n{bug_report["body"][0:100]}',
		username = send_user['username'],
		category = 'bugs'
	)

	return bug_report
