export default {
	by_rfid: async rfid =>
	{
		return await api(`
		query ($rfid: String!) {
			getBookByTag (rfid: $rfid) {
				__typename
				...on Book {
					title
					subtitle
					authors
					thumbnail
					description
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
				}
				...on BookTagDoesNotExistError {
					message
				}
			}
		}`, {
			rfid: rfid,
		})
	},

	get: async (filter, start, count, sorting) =>
	{
		return await api(`
		query ($filter: BookSearchFilter!, $start: Int!, $count: Int!, $sorting: Sorting!) {
			getBooks(filter: $filter, start: $start, count: $count, sorting: $sorting) {
				title
				subtitle
				authors
				description
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
			}
		}`, {
			filter: filter,
			start: start,
			count: count,
			sorting: sorting,
		})
	},

	count: async filter =>
	{
		return await api(`
		query ($filter: BookSearchFilter!) {
			countBooks(filter: $filter)
		}`, {
			filter: filter,
		})
	},
}