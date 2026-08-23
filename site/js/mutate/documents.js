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
	 * Create a new (empty) blob document.
	 * @param {string} title The document title.
	 * @returns {Promise<object>} The new document.
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
	 * Create a new blob document linked to an existing blob.
	 * @param {string} title The document title.
	 * @param {string} blob_id The ID of the blob.
	 * @returns {Promise<object>} The new document.
	 */
	link_blob: async (title, blob_id) => {
		return await api(`mutation ($title: String!, $blob_id: String!){
			linkBlobDocument (title: $title, blob_id: $blob_id){
				__typename
				...on Document { id }
				...on InsufficientPerms { message }
				...on BlobDocumentsNotSupported { message }
			}
		}`, {
			title,
			blob_id,
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

	/**
	 * Update tags on a document.
	 * @param {string} id The document ID.
	 * @param {array[string]} tag_list A list of tags to assign to this document.
	 * @returns {Promise<object>} The updated document.
	 */
	tags: async (id, tag_list) => {
		return await api(`
		mutation ($id: String!, $tags: [String!]!) {
			setDocumentTags (id: $id, tags: $tags) {
				__typename
				...on DocumentDoesNotExistError { message }
				...on InsufficientPerms { message }
			}
		}`, {
			id,
			tags: tag_list,
		})
	},
}
