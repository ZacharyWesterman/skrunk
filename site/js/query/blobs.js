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
	*/
	get: async (username, start, count, tag_query) =>
	{
		var res = await api(`
		query ($username: String, $start: Int!, $count: Int!, $tags: String){
			getBlobs(username: $username, start: $start, count: $count, tags: $tags) {
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
	*/
	count: async (username, tag_query) =>
	{
		return await api(`query ($username: String, $tags: String){
			countBlobs(username: $username, tags: $tags) {
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
