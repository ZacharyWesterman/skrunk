export default {
	/**
	 * Create a new document.
	 * @param {string} title The document title.
	 * @param {string} body The document body.
	 * @returns {Promise<object>} The new document.
	 */
	create: async (title, body) => {
		return await api(`mutation ($title: String!, $body: String!){
			createDocument (title: $title, body: $body){
				__typename
				...on Document { id }
				...on InsufficientPerms { message }
				...on DocumentDoesNotExistError { message }
			}
		}`, {
			title,
			body,
		})
	},

	/**
	 * Create a new (empty) blob document
	 */
	create_blob: async (title) => {
		return await api(`mutation ($title: String!){
			createBlobDocument (title: $title){
				__typename
				...on Document { id }
				...on InsufficientPerms { message }
				...on BlobDocumentsNotSupported { message }
			}
		}`, {
			title,
		})
	},

	/**
	 * Update a document.
	 * @param {string} id The document ID.
	 * @param {string?} title The new document title, or null if no change.
	 * @param {string?} body The new document body, or null if no change.
	 * @returns {Promise<object>} The updated document.
	 */
	update: async (id, title, body) => {
		return await api(`mutation ($id: String!, $title: String, $body: String){
			updateDocument (id: $id, title: $title, body: $body){
				__typename
				...on Document {
					id
					title
					creator {
						username
						display_name
					}
					created
				}
				...on InsufficientPerms { message }
				...on DocumentDoesNotExistError { message }
			}
		}`, {
			id,
			title,
			body,
		})
	},

	/**
	 * Delete a document.
	 * @param {string} id The document ID.
	 * @returns {Promise<object>} The deleted document.
	 */
	delete: async (id) => {
		return await api(`mutation ($id: String!){
			deleteDocument (id: $id) {
				__typename
				...on InsufficientPerms { message }
				...on DocumentDoesNotExistError { message }
			}
		}`, {
			id
		})
	},
}
