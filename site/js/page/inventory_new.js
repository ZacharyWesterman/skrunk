export async function init()
{
	const types = {
		id: 'type',
		default: '<Object Type>',
		class: 'fit',
		options: ['Hammer', 'Shovel'],
		append: true,
	}

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
		_('type', types),
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

export function wipe_fields()
{
	$('type').value = ''
	$('category').value = ''
	$('location').value = ''
	$('description').value = ''
	$('photo').wipe()
}

export async function submit()
{
	let valid = true
	for (const i of ['category', 'type', 'location'])
	{
		if ($.val(i) === '')
		{
			$.flash(i)
			if (valid) $(i).focus()
			valid = false
		}
	}

	if (!$('photo').blob_id)
	{
		$.flash('photo')
		if (valid) $('photo').focus()
		valid = false
	}

	if (!valid) return

	//On valid object, we want to wipe some fields, but not all.
	_.modal.checkmark()
	$('type').value = ''
	$('description').value = ''
	$('photo').wipe()
}