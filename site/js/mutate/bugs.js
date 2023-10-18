export default {
	report: async (text, plaintext = false) =>
	{
		return await api(`
		mutation ($text: String!, $plaintext: Boolean!) {
			reportBug (text: $text, plaintext: $plaintext) {
				__typename
				...on InsufficientPerms {
					message
				}
			}
		}`, {
			text: text,
			plaintext: plaintext,
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

	comment: async (id, text, plaintext = false) =>
	{
		return await api(`
		mutation ($id: String!, $text: String!, $plaintext: Boolean!) {
			commentOnBug (id: $id, text: $text, plaintext: $plaintext) {
				__typename
				...on BugReport {
					convo {
						created
						creator
						body
						body_html
					}
				}
				...on InsufficientPerms {
					message
				}
			}
		}`, {
			id: id,
			text: text,
			plaintext: plaintext,
		})
	},
}
