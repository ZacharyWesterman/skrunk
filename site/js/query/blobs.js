function prettify(blob)
{
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
	get: async (username, start, count, tag_query, date_from, date_to, name, sorting) =>
	{
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
			},
			start: start,
			count: count,
			sorting: sorting,
		})

		if (res.blobs)
		{
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
	count: async (username, tag_query, date_from, date_to, name) =>
	{
		return await api(`query ($filter: BlobSearchFilter!){
			countBlobs(filter: $filter) {
				__typename
				...on BlobCount {
					count
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
			},
		})
	},

	/**
	* username: string or null
	* tag_query: string or null
	* date_from: Date or null
	* date_to: Date or null
	*/
	size: async (username, tag_query, date_from, date_to, name) =>
	{
		return await api(`query ($filter: BlobSearchFilter!){
			totalBlobSize(filter: $filter) {
				__typename
				...on BlobCount {
					count
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
			},
		})
	},

	single: async blob_id =>
	{
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
			}
		}`, {
			id: blob_id,
		})

		return (blob.__typename === 'Blob') ? prettify(blob) : blob
	},
}
