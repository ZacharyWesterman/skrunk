export async function init()
{
	const categories = {
		id: 'category',
		default: '<Category>',
		class: 'fit',
		options: ['cat1', 'cat2'],
		append: true,
	}

	const locations = {
		id: 'location',
		default: '<Location>',
		class: 'fit',
		options: ['location1', 'location2'],
		append: true,
	}

	const promises = [
		_('category', categories),
		_('location', locations),
	]
	for (const i of promises) await i
}

export async function append_modal(field)
{
	const res = await _.modal({
		title: `Add ${field}`,
		text: `<input id="option-add" placeholder="${field}">`,
		buttons: ['OK', 'Cancel'],
	}, () => {}, choice => {
		if (choice === 'cancel') return true

		const value = $.val('option-add')
		if (value === '')
		{
			$.flash('option-add')
			return false
		}

		$(field).add(new Option(value, value, false, true))
		return true
	}).catch(() => 'cancel')
}