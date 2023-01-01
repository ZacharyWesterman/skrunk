export default {
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
}
