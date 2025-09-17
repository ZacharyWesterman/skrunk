export default {
	report: async (text) => {
		return await api(`
		mutation ($text: String!) {
			reportBug (text: $text) {
				__typename
				...on InsufficientPerms {
					message
				}
			}
		}`, {
			text: text,
		})
	},

	delete: async (id) => {
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

	resolve: async (id, status) => {
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

	comment: async (id, text) => {
		return await api(`
		mutation ($id: String!, $text: String!) {
			commentOnBug (id: $id, text: $text) {
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
		})
	},
}
