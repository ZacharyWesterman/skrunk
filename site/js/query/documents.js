export default {
	/**
	 * Get a document by its ID.
	 * @param {string} id The document ID.
	 * @returns {Promise<object>} The document.
	 */
	get: async (id) => {
		return await api(`query ($id: String!){
			getDocument (id: $id){
				id
				created
				creator
				title
				body
				body_html
			}
		}`, {
			id: id
		})
	},

	/**
	 * Retrieve child documents of a parent document. If parent_id is null, retrieve top-level documents.
	 * 
	 * @param {string?} parent_id The parent document ID, or null.
	 * @returns {Promise<object[]>} Array of minimal document objects.
	 */
	list: async (parent_id = null) => {
		return await api(`query ($id: String){
			getChildDocuments (id: $id){
				id
				title
			}
		}`, {
			id: parent_id
		})
	},
}
