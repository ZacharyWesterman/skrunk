export default {
	/**
	* username: string or null
	* start: int
	* count: int
	* resolved: boolean
	*/
	list: async (username, start, count, resolved) => {
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
			username,
			resolved,
			start,
			count,
		})
	},

	/**
	 * @brief Count the number of issues that exist.
	 * 
	 * @param {string|null} username The user who created the issue. If null, issues by any user are counted.
	 * @param {boolean} resolved Whether the issue is marked as resolved. If null, issues with any resolution status are counted.
	 * @return {Promise<int>} The number of issues matching the search criteria.
	 */
	count: async (username, resolved) => {
		return await api(`query ($username: String, $resolved: Boolean!) {
			countBugReports (username: $username, resolved: $resolved)	
		}`, {
			username,
			resolved,
		})
	}
}
