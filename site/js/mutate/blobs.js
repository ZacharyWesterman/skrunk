export default {
	delete: async blob_id =>
	{
		return await api(`
		mutation ($id: String!) {
			deleteBlob(id: $id) {
				__typename
				...on BlobDoesNotExistError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`, {id: blob_id})
	},

	tags: async (blob_id, tag_list) =>
	{
		return await api(`
		mutation ($id: String!, $tags: [String!]!) {
			setBlobTags (id: $id, tags: $tags) {
				__typename
				...on BlobDoesNotExistError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`, {
			id: blob_id,
			tags: tag_list,
		})
	},
}
