export async function submit_bug_report()
{
	if (!(await can_submit())) return

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

	_.modal.checkmark()

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

async function can_submit()
{
	if ($.val('new-bug-title') === '')
	{
		_.modal({
			type: 'error',
			title: 'Missing Information',
			text: 'Please fill out the Title and Description fields.',
			buttons: ['OK'],
		}).catch(() => {})
		return false
	}
	if ($.val('new-bug-text') === '')
	{
		const res = await _.modal({
			type: 'question',
			title: 'Submit without description?',
			text: 'Are you sure you want to submit a bug report with no description? Any information will be helpful to find and eliminate the bug.',
			buttons: ['Yes', 'No'],
		}).catch(() => 'no')

		if (res === 'no') return false
	}

	return true
}

export async function confirm_delete_bug(id, title)
{
	const choice = await _.modal({
		type: 'question',
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
		type: 'question',
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

export function load_open_issues()
{
	_('issues', api(`{
		getOpenIssues {
			title
			number
			labels {
				name
				color
			}
		}
	}`))
}
