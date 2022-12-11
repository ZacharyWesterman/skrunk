window.weather = {
	get_users: async function() {
		return await api(`{
			getWeatherUsers {
				username
				lat
				lon
				max {
					disable
					default
					value
				}
				min {
					disable
					default
					value
				}
				phone
				last_sent
				exclude
			}
		}`)
	},

	create_user: async function(username, lat, lon, phone, max, min) {
		const query = `mutation ($userdata: WeatherUserInput!){
			createWeatherUser(userdata: $userdata){
				__typename
				...on BadUserNameError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`
		const vars = {
			userdata: {
				username: username,
				lat: lat,
				lon: lon,
				max: max,
				min: min,
				phone: phone,
			}
		}
		return await api(query, vars)
	},

	delete_user: async function(username) {
		const query = `mutation ($username: String!){
			deleteWeatherUser(username: $username){
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
			username: username,
		}
		return await api(query, vars)
	},

	enable_user: async function(username) {
		const query = `mutation ($username: String!){
			enableWeatherUser(username: $username){
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
			username: username,
		}
		return await api(query, vars)
	},

	disable_user: async function(username) {
		const query = `mutation ($username: String!){
			disableWeatherUser(username: $username){
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
			username: username,
		}
		return await api(query, vars)
	},

	update_user: async function(username, phone, lat, lon, max, min) {
		const query = `mutation ($userdata: WeatherUserInput!){
			updateWeatherUser(userdata: $userdata){
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
			userdata: {
				username: username,
				lat: lat,
				lon: lon,
				phone: phone,
				max: max,
				min: min,
			}
		}
		return await api(query, vars)
	},
}
