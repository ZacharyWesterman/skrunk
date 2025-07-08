export default {
	/**
	 * Create a new document.
	 * @param {string} title The document title.
	 * @param {string} body The document body.
	 * @param {string?} parent_id The parent document ID, or null.
	 * @returns {Promise<object>} The new document.
	 */
	create: async (title, body, parent_id = null) => {
		return await api(`mutation ($title: String!, $body: String!, $parent_id: String){
			createDocument (title: $title, body: $body, parent_id: $parent_id){
				id
				created
				creator
				title
				body
				body_html
			}
		}`, {
			title: title,
			body: body,
			parent_id: parent_id
		})
	},

	/**
	 * Update a document.
	 * @param {string} id The document ID.
	 * @param {string?} title The new document title, or null if no change.
	 * @param {string?} body The new document body, or null if no change.
	 * @param {string?} parent_id The new parent document ID, or null if no change.
	 * @returns {Promise<object>} The updated document.
	 */
	update: async (id, title, body, parent_id) => {
		return await api(`mutation ($id: String!, $title: String, $body: String, $parent: String){
			updateDocument (id: $id, title: $title, body: $body, parent: $parent){
				id
				created
				creator
				title
				body
				body_html
			}
		}`, {
			id: id,
			title: title,
			body: body,
			parent: parent_id,
		})
	},

	/**
	 * Delete a document.
	 * @param {string} id The document ID.
	 * @returns {Promise<object>} The deleted document.
	 */
	delete: async (id) => {
		return await api(`mutation ($id: String!){
			deleteDocument (id: $id)
		}`, {
			id: id
		})
	},
}
