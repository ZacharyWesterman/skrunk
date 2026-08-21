export default {
	/**
	 * Get a document by its ID.
	 * @param {string} id The document ID.
	 * @returns {Promise<object>} The document.
	 */
	get: async (id) => {
		return await api(`query ($id: String!){
			getDocument (id: $id){
				__typename
				...on Document {
					id
					title
					creator {
						username
						display_name
					}
					created
					updater {
						username
						display_name
					}
					updated
				}
				...on InsufficientPerms { message }
				...on DocumentDoesNotExistError { message }
			}
		}`, {
			id: id
		})
	},

	/**
	 * Get a document's body text by its ID.
	 * 
	 * @param {string} id The document ID.
	 * @returns {Promise<object>} The document with the body html (if successful).
	 */
	get_body: async (id) => {
		const result = await api(`query ($id: String!){
			getDocument (id: $id){
				__typename
				...on Document { body_html }
				...on InsufficientPerms { message }
				...on DocumentDoesNotExistError { message }
			}
		}`, {
			id: id
		})

		return result
	},

	/**
	 * Retrieve a list of documents.
	 * 
	 * @param {int} start The starting point for pagination.
	 * @param {int} count The max number of documents to return.
	 * @returns {Promise<object[]>} Array of minimal document objects.
	 */
	list: async (start, count) => {
		return await api(`query ($start: Int!, $count: Int!) {
			getDocuments (start: $start, count: $count) {
				id
				title
				creator {
					username
					display_name
				}
				created
				updater {
					username
					display_name
				}
				updated
			}
		}`, {
			start,
			count,
		})
	},

	/**
	 * Count the total number of documents visible to this user.
	 * 
	 * @returns {Promise<int>} The total number of documents visible to this user.
	 */
	count: async () => {
		return await api(`{ countDocuments {
			__typename
			...on DocumentCount { count }
		} }`)
	},
}
