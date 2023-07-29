export default {
	/**
	* username: string or null
	* start: int
	* count: int
	* resolved: boolean
	*/
	list: async (username, start, count, resolved) =>
	{
		const bugs = await api(`query ($username: String, $start: Int!, $count: Int!, $resolved: Boolean!){
			getBugReports (username: $username, start: $start, count: $count, resolved: $resolved){
				id
				created
				creator
				body
				body_html
				convo
				resolved
			}
		}`, {
			username: username,
			resolved: resolved,
			start: start,
			count: count,
		})

		return bugs.filter(bug => {
			bug.created = date.output(bug.created)
			return bug
		})
	},
}
