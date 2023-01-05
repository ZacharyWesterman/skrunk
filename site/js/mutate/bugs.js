export default {
	report: async (title, text) =>
	{
		return await api(`
		mutation ($title: String!, $text: String!) {
			reportBug (title: $title, text: $text) {
				__typename
			}
		}`, {
			title: title,
			text: text,
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
}
