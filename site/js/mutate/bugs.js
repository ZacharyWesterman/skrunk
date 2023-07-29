export default {
	report: async (text, html) =>
	{
		return await api(`
		mutation ($text: String!, $html: String!) {
			reportBug (text: $text, html: $html) {
				__typename
			}
		}`, {
			text: text,
			html: html,
		})
	},

	delete: async (id) =>
	{
		return await api(`
		mutation ($id: String!) {
			deleteBug (id: $id) {
				__typename
				...on BugReportDoesNotExistError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`, {
			id: id,
		})
	},

	resolve: async (id, status) =>
	{
		return await api(`
		mutation ($id: String!, $status: Boolean!) {
			setBugStatus(id: $id, status: $status) {
				__typename
				...on BugReportDoesNotExistError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`, {
			id: id,
			status: status,
		})
	},
}
