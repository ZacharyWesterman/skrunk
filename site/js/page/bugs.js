await mutate.require('bugs')
await query.require('bugs')

export function init()
{
	const old_modal_retn = _.modal.upload.return
	_.modal.upload.return = () => {
		const id_list = old_modal_retn()
		navigator.clipboard.writeText(`${window.location}blob/${id_list[0].id+id_list[0].ext}`).then(() => {
			_.modal({
				text: 'Copied URL to clipboard!',
			}).catch(() => {})
			setTimeout(_.modal.cancel, 800)
		})
	}

	window.unload.push(() => {
		_.modal.upload.return = old_modal_retn
	})
}

export async function submit_bug_report()
{
	if (!(await can_submit())) return

	$.toggle_expand('card-new-bug')

	const res = await mutate.bugs.report(
		$('new-bug-text').value,
		await $.editor.md_to_html($('new-bug-text').value),
	)

	if (res.__typename !== 'BugReport')
	{
		$.toggle_expand('card-new-bug')

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

	refresh_bug_list()
}

export async function refresh_bug_list()
{
	const bugs = await query.bugs.list(null, 0, 100, false)
	await _('buglist', bugs)
}

export function open_editor()
{
	$.editor.open($.val('new-bug-text')).then(result => {
		$('new-bug-text').value = result.text
	}).catch(() => {})
}

async function can_submit()
{
	if ($.val('new-bug-text') === '')
	{
		_.modal({
			type: 'error',
			title: 'Missing Information',
			text: 'Please put something in the description.',
			buttons: ['OK'],
		}).catch(() => {})
		return false
	}

	return true
}

export async function confirm_delete_bug(id, title)
{
	const choice = await _.modal({
		type: 'question',
		title: 'Delete Bug Report?',
		text: `This bug report will be permanently removed from the list.`,
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
