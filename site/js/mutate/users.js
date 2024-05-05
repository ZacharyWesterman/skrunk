export default {
	delete: async username =>
	{
		const query = `
		mutation ($username: String!){
			deleteUser(username: $username) {
				__typename
				...on UserDoesNotExistError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`
		const vars = {
			'username' : username,
		}
		return await api(query, vars)
	},

	create: async (username, pass_hash, groups) =>
	{
		const query = `
		mutation ($username: String!, $password: String!, $groups: [String!]!){
			createUser(username: $username, password: $password, groups: $groups) {
				__typename
				...on BadUserNameError {
					message
				}
				...on UserExistsError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`
		const vars = {
			'username': username,
			'password': pass_hash,
			'groups': groups || [],
		}
		return await api(query, vars)
	},

	revoke: async username =>
	{
		return await api(`
		mutation ($username: String!) {
			revokeSessions (username: $username)
		}`, {
			username: username,
		})
	},

	permissions: async (username, permission_list) =>
	{
		const query = `
		mutation ($username: String!, $perms: [String!]!){
			updateUserPerms(username: $username, perms: $perms) {
				__typename
				...on UserDoesNotExistError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`
		const vars = {
			'username' : username,
			'perms': permission_list,
		}
		return await api(query, vars)
	},

	password: async (username, pass_hash) =>
	{
		return await api(`mutation ($username: String!, $password: String!) {
			updateUserPassword(username: $username, password: $password) {
				__typename
				...on UserDoesNotExistError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`, {
			username: username,
			password: pass_hash,
		})
	},

	display_name: async (username, disp_name) =>
	{
		return await api(`mutation ($username: String!, $display_name: String!) {
			updateUserDisplayName (username: $username, display_name: $display_name) {
				__typename
				...on UserData {
					display_name
				}
				...on UserDoesNotExistError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`, {
			'username': username,
			'display_name': disp_name,
		})
	},

	module: async (username, module_name, disabled) =>
	{
		return await api(`mutation ($username: String!, $module: String!, $disabled: Boolean!) {
			updateUserModule (username: $username, module: $module, disabled: $disabled) {
				__typename
				...on UserData { disabled_modules }
				...on UserDoesNotExistError { message }
				...on InsufficientPerms { message }
			}
		}`, {
			username: username,
			module: module_name,
			disabled: disabled,
		})
	},
}
