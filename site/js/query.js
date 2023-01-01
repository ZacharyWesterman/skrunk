import Weather from "/js/query/weather.js"
import Users from "/js/query/users.js"
import Blobs from "/js/query/blobs.js"
import Bugs from "/js/query/bugs.js"

window.query = {
	weather: Weather,
	users: Users,
	blobs: Blobs,
	bugs: Bugs,
}
