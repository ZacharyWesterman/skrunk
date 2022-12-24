export async function submit_bug_report()
{
	const res = await api(`mutation ($title: String!, $text: String!) {
		reportBug (title: $title, text: $text)
	}`, {
		title: $('new-bug-title').value,
		text: $('new-bug-text').value,
	})

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
	let bugs = await api(`query ($username: String, $start: Int!, $count: Int!, $resolved: Boolean!){
		getBugReports (username: $username, start: $start, count: $count, resolved: $resolved){
			id
			created
			creator
			title
			body
			convo
			resolved
		}
	}`, {
		username: null, //list everyone's bug reports
		resolved: false,
		start: 0,
		count: 100,
	})

	bugs = bugs.filter(bug => {
		bug.created = date.output(bug.created)
		return bug
	})
	
	await _('buglist', bugs)
}

export function check_can_submit()
{
	$('new-bug-submit').disabled = ($.val('new-bug-title') === '') || ($.val('new-bug-text') === '')
}