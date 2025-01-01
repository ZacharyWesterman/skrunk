function prettify(blob) {
	blob.created = date.output(blob.created) //convert dates to local time
	blob.size = format.file_size(blob.size) //convert size to human-readable format
	return blob
}

export default {
	/**
	* username: string or null
	* start: int
	* count: int
	* tag_query: string or null
	* date_from: Date or null
	* date_to: Date or null
	*/
	get: async (username, start, count, tag_query, date_from, date_to, name, ephemeral, sorting) => {
		let res = await api(`
		query ($filter: BlobSearchFilter!, $start: Int!, $count: Int!, $sorting: Sorting!){
			getBlobs(filter: $filter, start: $start, count: $count, sorting: $sorting) {
				__typename
				...on BlobList {
					blobs {
						id
						ext
						mimetype
						name
						size
						creator
						created
						tags
						preview
						thumbnail
						hidden
						ephemeral
						references
					}
				}
				...on BadTagQuery {
					message
				}
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
			start: start,
			count: count,
			sorting: sorting,
		})

		if (res.blobs) {
			res.blobs = res.blobs.map(prettify)
		}

		return res
	},

	/**
	* username: string or null
	* tag_query: string or null
	* date_from: Date or null
	* date_to: Date or null
	*/
	count: async (username, tag_query, date_from, date_to, name, ephemeral) => {
		return await api(`query ($filter: BlobSearchFilter!){
			countBlobs(filter: $filter) {
				__typename
				...on BlobCount { count }
				...on BadTagQuery { message }
				...on InsufficientPerms { message }
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
		})
	},

	/**
	 * Get the total size of all files matching the given criteria.
	 * @param {string?} username The user who uploaded, or null for all users in the same group.
	 * @param {string?} tag_query A tag query expression, if any.
	 * @param {Date?} date_from The start date, or null to include any upload date <= the end date.
	 * @param {Date?} date_to The end date, or null to include any upload date >= the start date.
	 * @param {boolean?} ephemeral Whether ephemeral files are included.
	 * @returns The sum total size of all files that match the criteria, in bytes. 
	 */
	size: async (username, tag_query, date_from, date_to, name, ephemeral) => {
		return await api(`query ($filter: BlobSearchFilter!){
			totalBlobSize(filter: $filter) {
				__typename
				...on BlobCount { count }
				...on BadTagQuery { message }
				...on InsufficientPerms { message }
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
		})
	},

	single: async blob_id => {
		const blob = await api(`
		query ($id: String!){
			getBlob (id: $id) {
				id
				ext
				mimetype
				name
				size
				creator
				created
				tags
				preview
				thumbnail
				hidden
				ephemeral
			}
		}`, {
			id: blob_id,
		})

		return (blob.__typename === 'Blob') ? prettify(blob) : blob
	},
}
