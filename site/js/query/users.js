export default {
	list: async () => await api('{listUsers}'),

	sessions: async username =>
	{
		return await api(`query ($username: String!) {
			countSessions (username: $username)
		}`, {
			username: username,
		})
	},

	get: async username =>
	{
		return await api(`query ($username: String!){
			getUser(username:$username) {
				__typename
				...on UserData {
					username
					theme {
						colors {
							name
							value
						}
						sizes {
							name
							value
						}
					}
					perms
				}
				...on UserDoesNotExistError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`, {
			username: username
		})
	},
}
