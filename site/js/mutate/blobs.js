export default {
	delete: async blob_id => {
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
		}`, { id: blob_id })
	},

	tags: async (blob_id, tag_list) => {
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

	create_zip: async (username, tag_query, date_from, date_to, name, ephemeral, uid) => {
		return await api(`
		mutation ($filter: BlobSearchFilter!, $uid: String!) {
			createZipArchive (filter: $filter, uid: $uid) {
				__typename
				...on Blob {
					id
					ext
					name
					size
				}
				...on BadTagQuery { message }
				...on UserDoesNotExistError { message }
				...on InsufficientPerms { message }
				...on InsufficientDiskSpace { message }
				...on BlobDoesNotExistError { message }
			}
		}`, {
			filter: {
				creator: username,
				tag_expr: tag_query,
				begin_date: date.db_output(date_from),
				end_date: date.db_output(date_to),
				name: name,
				ephemeral: ephemeral,
			},
			uid: uid,
		})
	},

	set_hidden: async (blob_id, hidden) => {
		return await api(`
		mutation ($id: String!, $hidden: Boolean!) {
			setBlobHidden (id: $id, hidden: $hidden) {
				__typename
				...on Blob {
					hidden
				}
				...on BlobDoesNotExistError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`, {
			id: blob_id,
			hidden: hidden,
		})
	},

	set_ephemeral: async (blob_id, ephemeral) => {
		return await api(`mutation ($id: String!, $ephemeral: Boolean!) {
			setBlobEphemeral (id: $id, ephemeral: $ephemeral) {
				__typename
				...on BlobDoesNotExistError { message }
				...on InsufficientPerms { message }
			}
		}`, {
			id: blob_id,
			ephemeral: ephemeral,
		})
	},
}
