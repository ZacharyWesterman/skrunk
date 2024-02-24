let LookupStart = 0
let LookupListLen = 15

export async function init()
{
	await _('lookup', {
		header: 'Search for items:',
		fields: '',
		template: 'inventory-items',
	})

	navigate_to_page(1)
}

export async function navigate_to_page(page_num)
{
	const count_promise = api(`query ($filter: InventorySearchFilter!) {
		countInventory(filter: $filter)
	}`, {
		filter: {},
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
		filter: {}, //No filter currently
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
