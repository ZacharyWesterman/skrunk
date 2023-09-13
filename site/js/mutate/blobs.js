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

	create_zip: async (username, tag_query, date_from, date_to, name) =>
	{
		return await api(`
		mutation ($filter: BlobSearchFilter!) {
			createZipArchive (filter: $filter) {
				__typename
				...on Blob {
					id
					ext
					name
					size
				}
				...on BadTagQuery { message }
				...on UserDoesNotExistError { message }
			}
		}`, {
			filter: {
				creator: username,
				tag_expr: tag_query,
				begin_date: date.db_output(date_from),
				end_date: date.db_output(date_to),
				name: name,
			}
		})
	},
}
