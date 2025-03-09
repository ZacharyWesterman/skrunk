export default {
	by_rfid: async rfid => {
		return await api(`
		query ($rfid: String!) {
			getBookByTag (rfid: $rfid) {
				__typename
				...on Book {
					title
					subtitle
					authors
					thumbnail
					has_description
					owner {
						username
						display_name
					}
					id
					rfid
					categories
					shared
					shareHistory {
						user_id
						name
						display_name
					}
					industryIdentifiers {
						type
						identifier
					}
					ebooks {
						url
						fileType
					}
					audiobook
				}
				...on BookTagDoesNotExistError {
					message
				}
			}
		}`, {
			rfid: rfid,
		})
	},

	get: async (filter, start, count, sorting) => {
		return await api(`
		query ($filter: BookSearchFilter!, $start: Int!, $count: Int!, $sorting: Sorting!) {
			getBooks(filter: $filter, start: $start, count: $count, sorting: $sorting) {
				title
				subtitle
				authors
				has_description
				thumbnail
				owner {
					username
					display_name
				}
				id
				rfid
				categories
				shared
				shareHistory {
					user_id
					name
					display_name
				}
				industryIdentifiers {
					type
					identifier
				}
				ebooks {
					url
					fileType
				}
				audiobook
			}
		}`, {
			filter: filter,
			start: start,
			count: count,
			sorting: sorting,
		})
	},

	get_description: async id => {
		return await api(`
		query ($id: String!) {
			getBookDescription(id: $id)
		}`, {
			id: id,
		})
	},

	count: async filter => {
		return await api(`
		query ($filter: BookSearchFilter!) {
			countBooks(filter: $filter)
		}`, {
			filter: filter,
		})
	},
}
