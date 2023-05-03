export async function submit_bug_report()
{
	if (!can_submit()) return

	const res = await mutate.bugs.report(
		$('new-bug-title').value,
		$('new-bug-text').value,
	)

	if (res.__typename !== 'BugReport')
	{
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: 'Failed to submit bug report!',
			buttons: ['OK']
		}).catch(() => {})
		return
	}

	$('new-bug-text').value = ''
	$('new-bug-title').value = ''
	$.toggle_expand('card-new-bug')

	refresh_bug_list()
}

export async function refresh_bug_list()
{
	const bugs = await query.bugs.list(null, 0, 100, false)
	await _('buglist', bugs)
}

function can_submit()
{
	return ($.val('new-bug-title') !== '') && ($.val('new-bug-text') !== '')
}

export async function confirm_delete_bug(id, title)
{
	const choice = await _.modal({
		title: 'Delete Bug Report?',
		text: `"${title}" will be permanently removed from the list.`,
		buttons: ['Yes', 'No']
	}).catch(() => 'no')

	if (choice !== 'yes') return

	const res = await mutate.bugs.delete(id)
	if (res.__typename !== 'BugReport')
	{
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK']
		}).catch(() => {})
		return
	}

	await refresh_bug_list()
}

export async function confirm_resolve_bug(id)
{
	const choice = await _.modal({
		title: 'Mark bug report as resolved?',
		text: 'This will hide the report from the list of outstanding bugs, but will not delete it.',
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (choice !== 'yes') return

	const res = await mutate.bugs.resolve(id, true)
	if (res.__typename !== 'BugReport')
	{
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK']
		}).catch(() => {})
		return
	}

	await refresh_bug_list()
}
