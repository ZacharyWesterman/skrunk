await mutate.require('bugs')
await query.require('bugs')

let EDITORS = {}

export function editor(id)
{
	return EDITORS[id]
}
editor.new = id => EDITORS[id] = new SimpleMDE({element: $(id)})
editor.del = id => delete EDITORS[id]

export function init()
{
	const old_modal_retn = _.modal.upload.return
	_.modal.upload.return = () => {
		const id_list = old_modal_retn()
		if (id_list === undefined) return

		navigator.clipboard.writeText(`${window.location.href.split('?')[0]}blob/${id_list[0].id+id_list[0].ext}`).then(() => {
			_.modal({
				text: 'Copied URL to clipboard!',
				no_cancel: true,
			}).catch(() => {})
			setTimeout(_.modal.cancel, 800)
		})
	}

	window.unload.push(() => {
		_.modal.upload.return = old_modal_retn
		EDITORS = {}
	})

	editor.new('new-bug-text')
}

export async function submit_bug_report()
{
	if (!(await can_submit())) return

	$.toggle_expand('card-new-bug')

	const res = await mutate.bugs.report(editor('new-bug-text').value())

	if (res.__typename !== 'BugReport')
	{
		$.toggle_expand('card-new-bug')
		_.modal.error(res.message)
		return
	}

	_.modal.checkmark()

	editor('new-bug-text').value('')

	refresh_bug_list()
}

export function refresh_bug_list()
{
	_('open-bugs', {
		list: query.bugs.list(null, 0, 100, false),
		locked: false,
		bug_type: 'Outstanding',
		expanded: true,
	})
	_('resolved-bugs', {
		list: query.bugs.list(null, 0, 5, true),
		locked: true,
		bug_type: 'Resolved',
		expanded: false,
	})
}

export async function comment_on_bug_report(bug_id)
{
	const text = editor(`text-${bug_id}`).value()
	if (text === '') return

	$.toggle_expand(`newcomment-${bug_id}`)

	const res = await mutate.bugs.comment(bug_id, text)

	if (res.__typename !== 'BugReport')
	{
		$.toggle_expand(`newcomment-${bug_id}`)

		_.modal({
			type: 'error',
			title: 'ERROR',
			text: 'Failed to comment on bug report!',
			buttons: ['OK'],
		}).catch(() => {})
		return
	}

	editor(`text-${bug_id}`).value('')
	_.modal.checkmark()

	if (!$(`comments-inner-${bug_id}`))
	{
		refresh_bug_list()
		return
	}

	let html_content = '<hr>'
	for (const comment of res.convo)
	{
		html_content += `
		<blockquote>
			<div class="disabled">
				${comment.creator} @ ${date.short(comment.created)}
			</div>
			${image_restrict(comment.body_html)}
		</blockquote>`
	}
	$(`comments-inner-${bug_id}`).innerHTML = html_content
}

async function can_submit()
{
	if (editor('new-bug-text').value() === '')
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
		text: `This bug report will be permanently removed from the list.<br><br><b>This action is permanent!</b>`,
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
				description
			}
		}
	}`))

	_('pending-issues', api(`{
		getPendingIssues {
			title
			number
			labels {
				name
				color
				description
			}
		}
	}`))
}
