export async function init()
{
	const categories = {
		id: 'category',
		default: '<Category>',
		class: 'fit',
		options: api(`{ getItemCategories }`),
		append: true,
	}

	let types = {
		id: 'type',
		default: '<Object Type>',
		class: 'fit',
		options: [],
		append: true,
	}

	const locations = {
		id: 'location',
		default: '<Location>',
		class: 'fit',
		options: api(`query ($owner: String!) {
			getItemLocations (owner: $owner)
		}`,{
			owner: api.username,
		}),
		append: true,
	}

	const promises = [
		_('_category', categories).then(() => {
			$.bind('category', () => {
				types.options = api(`query ($category: String!) {
					getItemTypes (category: $category)
				}`, {
					category: $.val('category'),
				})
				_('_type', types)
			})
		}),
		_('_type', types),
		_('_location', locations),
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

	const rfid = await modal.scanner()
	if (rfid === null) return

	const res = await api(`mutation ($category: String!, $type: String!, $location: String!, $blob_id: String!, $description: String!, $rfid: String!) {
		createInventoryItem (category: $category, type: $type, location: $location, blob_id: $blob_id, description: $description, rfid: $rfid) {
			__typename
			...on InsufficientPerms { message }
			...on InvalidFields { message fields }
		}
	}`, {
		category: $.val('category'),
		type: $.val('type'),
		location: $.val('location'),
		blob_id: $('photo').blob_id,
		description: $.val('description'),
		rfid: rfid,
	})

	if (res.__typename !== 'Item')
	{
		if (res.__typename === 'InvalidFields')
		{
			const message = res.message + '<ul>' + res.fields.map(i => `<li>${i}</li>`).join('') + '</ul>'
			$.modal.error(message)
		}
		else
		{
			$.modal.error(res.message)
		}
		return
	}

	//On valid object, we want to wipe some fields, but not all.
	_.modal.checkmark()
	$('type').value = ''
	$('description').value = ''
	$('photo').clear()
}
