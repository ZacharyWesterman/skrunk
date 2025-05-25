"""application.db.bugs"""

import html
from datetime import datetime

import markdown
from bson.objectid import ObjectId
from pymongo.collection import Collection

from application import exceptions

from . import notification, users
from .perms import caller_info_strict

## A pointer to the bug reports collection in the database.
db: Collection = None  # type: ignore[assignment]


def report_bug(text: str, plaintext: bool = True) -> dict:
	"""
	Report a new bug to the database.

	Args:
		text (str): The content of the bug report.
		plaintext (bool, optional): If True, the text is treated as plain text and escaped for HTML. 
									If False, the text is treated as Markdown and converted to HTML. 
									Defaults to True.

	Returns:
		dict: A dictionary containing the bug report details, including the newly assigned bug report ID.
	"""
	user_data = caller_info_strict()

	bug_report = {
		'created': datetime.utcnow(),
		'creator': user_data['_id'],
		'body': text,
		'body_html': html.escape(text) if plaintext else markdown.markdown(text, output_format='html'),
		'convo': [],
		'resolved': False,
	}

	id = db.insert_one(bug_report).inserted_id
	bug_report['_id'] = id

	return process_bug_report(bug_report)


def comment_on_bug(id: str, text: str, plaintext: bool = True) -> dict:
	"""
	Add a comment to a bug report.

	Args:
		id (str): The unique identifier of the bug report.
		text (str): The content of the comment.
		plaintext (bool, optional): If True, the comment is treated as plain text. 
									If False, the comment is treated as Markdown. Defaults to True.

	Returns:
		dict: The updated bug report.

	Raises:
		BugReportDoesNotExistError: If the bug report with the given id does not exist.
	"""
	user_data = caller_info_strict()

	report = db.find_one({'_id': ObjectId(id)})
	if report is None:
		raise exceptions.BugReportDoesNotExistError(id)

	convo_data = {
		'created': datetime.utcnow(),
		'creator': user_data['_id'],
		'body': text,
		'body_html': html.escape(text) if plaintext else markdown.markdown(text, output_format='html'),
	}

	db.update_one({'_id': ObjectId(id)}, {
		'$push': {'convo': convo_data}
	})

	report['convo'] += [convo_data]

	# Let all involved users know that the bug report has a new comment!
	# Make sure to include the user that created the bug report, even if they didn't comment on it.
	for i in list(set([i['creator'] for i in report['convo']] + [user_data['_id']])):
		# Don't send a notification if the user commented on their own bug report
		if i == user_data['_id']:
			continue

		this_user = users.get_user_by_id(i)
		whose = 'your' if i == report['creator'] else (this_user['display_name'] + "'s")

		notification.send(
			title=f'{user_data["display_name"]} commented on {whose} bug report',
			body=text[0:100],
			username=this_user['username'],
			category='bugs'
		)

	return process_bug_report(report)


def process_bug_report(report: dict) -> dict:
	"""
	Prepares a bug report database item for display by
	populating the report's creator and comments with usernames.

	Args:
		report (dict): A dictionary containing the bug report details. 
					   Expected keys are '_id', 'creator', and 'convo'.
					   'convo' is a list of comments, each with a 'creator' key.

	Returns:
		dict: The processed bug report with updated 'id', 'creator', and 'convo' fields.
			  The 'id' field is set to the value of '_id'.
			  The 'creator' field is updated to the username if the user exists, 
			  otherwise it is converted to a string.
			  Each comment's 'creator' field is similarly updated.
	"""
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
	"""
	Retrieve a bug report from the database by its ID.

	Args:
		id (str): The unique identifier of the bug report.

	Returns:
		dict: The processed bug report data.

	Raises:
		BugReportDoesNotExistError: If no bug report with the given ID is found.
	"""
	report = db.find_one({'_id': ObjectId(id)})
	if report is None:
		raise exceptions.BugReportDoesNotExistError(id)

	return process_bug_report(report)


def get_bug_reports(userids: list, start: int, count: int, resolved: bool) -> list:
	"""
	Retrieve a list of bug reports from the database.

	Args:
		userids (list): A list of user IDs to filter the bug reports by creator.
		start (int): The starting index for pagination.
		count (int): The number of bug reports to retrieve.
		resolved (bool): A flag indicating whether to retrieve resolved or unresolved bug reports.

	Returns:
		list: A list of processed bug reports.
	"""
	reports = []
	if len(userids) == 0:
		selection = db.find({'resolved': resolved}, sort=[('created', -1)])
	else:
		selection = db.find({
			'resolved': resolved,
			'$or': [{'creator': i} for i in userids],
		}, sort=[('created', -1)])

	for i in selection.limit(count).skip(start):
		reports += [process_bug_report(i)]

	return reports


def count_bug_reports(userids: list, resolved: bool) -> int:
	"""
	Count the number of bug reports based on the given user IDs and resolution status.

	Args:
		userids (list): A list of user IDs to filter the bug reports. If the list is empty, 
						the count will be based only on the resolution status.
		resolved (bool): The resolution status to filter the bug reports.

	Returns:
		int: The count of bug reports that match the given criteria.
	"""
	if len(userids) == 0:
		return db.count_documents({'resolved': resolved})

	return db.count_documents({
		'resolved': resolved,
		'$or': [{'creator': i} for i in userids],
	})


def delete_bug_report(id: str) -> dict:
	"""
	Deletes a bug report from the database by its ID.

	Args:
		id (str): The ID of the bug report to delete.

	Returns:
		dict: The deleted bug report with its ID included.

	Raises:
		BugReportDoesNotExistError: If no bug report with the given ID exists.
	"""
	bug_report = db.find_one({'_id': ObjectId(id)})
	if bug_report is None:
		raise exceptions.BugReportDoesNotExistError(id)

	db.delete_one({'_id': ObjectId(id)})
	bug_report['id'] = bug_report['_id']
	return bug_report


def set_bug_status(id: str, status: bool) -> dict:
	"""
	Update the status of a bug report and notify the creator.

	Args:
		id (str): The unique identifier of the bug report.
		status (bool): The new status of the bug report. True for resolved, False for reopened.

	Returns:
		dict: The updated bug report.

	Raises:
		exceptions.BugReportDoesNotExistError: If the bug report with the given id does not exist.
	"""
	bug_report = db.find_one({'_id': ObjectId(id)})
	if bug_report is None:
		raise exceptions.BugReportDoesNotExistError(id)

	db.update_one({'_id': ObjectId(id)}, {'$set': {'resolved': status}})
	bug_report['resolved'] = status

	user_data = caller_info_strict()

	send_user = users.get_user_by_id(bug_report['creator'])

	bug_status = "resolved" if status else "reopened"
	body = bug_report["body"][0:100]

	notification.send(
		title=f'A bug has been {"resolved" if status else "reopened"}',
		body=f'{user_data["display_name"]} has {bug_status} the issue you reported:\n{body}',
		username=send_user['username'],
		category='bugs'
	)

	return bug_report
