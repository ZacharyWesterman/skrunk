window.submit_bug_report = async () => {
	const report_text = $('new-bug-text').value
	if (report_text === '') return

	const res = await api(`mutation ($text: String!) {
		reportBug (text: $text)
	}`, {
		text: report_text
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
}

window.unload.push(() => {
	delete window.submit_bug_report
})
