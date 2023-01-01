export async function submit_bug_report()
{
	const res = await mutate.bugs.report(
		$('new-bug-title').value,
		$('new-bug-text').value,
	)

	if (!res)
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
	$.toggle_expand('card-new-bug')

	refresh_bug_list()
}

export async function refresh_bug_list()
{
	const bugs = await query.bugs.list(null, 0, 100, false)
	await _('buglist', bugs)
}

export function check_can_submit()
{
	$('new-bug-submit').disabled = ($.val('new-bug-title') === '') || ($.val('new-bug-text') === '')
}
