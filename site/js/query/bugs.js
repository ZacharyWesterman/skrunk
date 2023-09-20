export default {
	/**
	* username: string or null
	* start: int
	* count: int
	* resolved: boolean
	*/
	list: async (username, start, count, resolved) =>
	{
		return await api(`query ($username: String, $start: Int!, $count: Int!, $resolved: Boolean!){
			getBugReports (username: $username, start: $start, count: $count, resolved: $resolved){
				id
				created
				creator
				body
				body_html
				convo {
					created
					creator
					body
					body_html
				}
				resolved
			}
		}`, {
			username: username,
			resolved: resolved,
			start: start,
			count: count,
		})
	},
}
