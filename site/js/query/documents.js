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
					tags
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
	 * @param {object} filter The filtering inputs.
	 * @param {int} start The starting point for pagination.
	 * @param {int} count The max number of documents to return.
	 * @returns {Promise<object>} Array of document objects.
	 */
	list: async (filter, start, count) => {
		return await api(`query ($filter: DocumentSearchFilter!, $start: Int!, $count: Int!) {
			getDocuments (filter: $filter, start: $start, count: $count) {
				__typename
				...on DocumentList {
					documents {
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
						blob_id
						tags
					}
				}
				...on BadTagQuery { message }
			}
		}`, {
			filter,
			start,
			count,
		})
	},

	/**
	 * Count the total number of documents visible to this user.
	 * 
	 * @param {object} filter The filtering inputs.
	 * @returns {Promise<int>} The total number of documents visible to this user.
	 */
	count: async (filter) => {
		return await api(`query ($filter: DocumentSearchFilter!) {
			countDocuments (filter: $filter) {
				__typename
				...on DocumentCount { count }
				...on BadTagQuery { message }
			}
		}`, {
			filter,
		})
	},
}
