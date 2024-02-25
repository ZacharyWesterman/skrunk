let LookupStart = 0
let LookupListLen = 15

export async function init()
{
	await _('lookup', {
		header: 'Search for items:',
		fields: `
		<div name="owner" template="dropdown"></div>
		<div name="_category" template="dropdown"></div>
		<div name="_type" template="dropdown"></div>
		<div name="_location" template="dropdown"></div>
		`,
		template: 'inventory-items',
	})

	const categories = {
		id: 'category',
		default: '<Category>',
		class: 'fit',
		options: api(`{ getItemCategories }`),
	}

	let types = {
		id: 'type',
		default: '<Object Type>',
		class: 'fit',
		options: [],
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
	}

	const users = {
		id: 'owner',
		default: '<Owner>',
		class: 'fit',
		options: query.users.list(),
	}

	const bind = field => {return () => $.bind(field, () => navigate_to_page(0)) }

	const promises = [
		_('owner', users).then(bind('owner')),
		_('_category', categories).then(() => {
			$.bind('category', () => {
				types.options = api(`query ($category: String!) {
					getItemTypes (category: $category)
				}`, {
					category: $.val('category'),
				})
				_('_type', types).then(bind('type'))
				navigate_to_page(0)
			})
		}),
		_('_type', types),
		_('_location', locations).then(bind('location')),
	]
	for (const i of promises) await i

	navigate_to_page(1)
}

export async function navigate_to_page(page_num)
{
	const filter = {
		category: $.val('category') || null,
		type: $.val('type') || null,
		location: $.val('location') || null,
		owner: $.val('owner') || null,
	}

	const count_promise = api(`query ($filter: InventorySearchFilter!) {
		countInventory(filter: $filter)
	}`, {
		filter: filter,
	}).then(res => {
		const count = res

		const page_ct = Math.ceil(count / LookupListLen)
		const pages = Array.apply(null, Array(page_ct)).map(Number.call, Number)
		let this_page = Math.floor(LookupStart / LookupListLen)
		if (page_ct === 0)
		{
			this_page = LookupStart = 0
		}
		else if (this_page >= page_ct)
		{
			this_page = page_ct - 1
			LookupStart = this_page * LookupListLen
		}

		return {
			pages: pages,
			count: page_ct,
			current: this_page,
			total: count,
			no_results_msg: 'No results found matching the search criteria.',
		}
	})

	const items_promise = api(`query ($filter: InventorySearchFilter!, $start: Int!, $count: Int!, $sorting: Sorting!) {
		getInventory (filter: $filter, start: $start, count: $count, sorting: $sorting) {
			id
			category
			type
			location
			blob {
				thumbnail
			}
			created
			creator {
				username
				display_name
			}
			description_html
		}
	}`, {
		filter: filter,
		start: LookupStart,
		count: LookupListLen,
		sorting: {
			fields: ['category', 'type', 'location'],
			descending: true,
		}
	})

	await _('page-list', count_promise)
	await _('lookup-results', items_promise)
}
