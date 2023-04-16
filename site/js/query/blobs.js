function prettify(blob)
{
	blob.created = date.output(blob.created) //convert dates to local time

	var sizes = ['GB', 'MB', 'KB']
	var sizetype = 'B'
	while (blob.size >= 1000)
	{
		sizetype = sizes.pop()
		blob.size /= 1000
	}
	blob.size = blob.size.toFixed(2) + ' ' + sizetype //convert size to human-readable format
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
	get: async (username, start, count, tag_query, date_from, date_to, name) =>
	{
		var res = await api(`
		query ($username: String, $start: Int!, $count: Int!, $tags: String, $beginDate: DateTime, $endDate: DateTime, $name: String){
			getBlobs(username: $username, start: $start, count: $count, tags: $tags, beginDate: $beginDate, endDate: $endDate, name: $name) {
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
					}
				}
				...on BadTagQuery {
					message
				}
			}
		}`, {
			username: username,
			start: start,
			count: count,
			tags: tag_query,
			beginDate: date.db_output(date_from),
			endDate: date.db_output(date_to),
			name: name,
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
		return await api(`query ($username: String, $tags: String, $beginDate: DateTime, $endDate: DateTime, $name: String){
			countBlobs(username: $username, tags: $tags, beginDate: $beginDate, endDate: $endDate, name: $name) {
				__typename
				...on BlobCount {
					count
				}
				...on BadTagQuery {
					message
				}
			}
		}`, {
			username: username,
			tags: tag_query,
			beginDate: date.db_output(date_from),
			endDate: date.db_output(date_to),
			name: name,
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
