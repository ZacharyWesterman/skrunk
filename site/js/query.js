const Imports = {
	weather: import('/js/query/weather.js'),
	users: import('/js/query/users.js'),
	blobs: import('/js/query/blobs.js'),
	bugs: import('/js/query/bugs.js'),
}

let Query = {}
for (const i in Imports)
{
	const module = await Imports[i]
	Query[i] = module.default
}
window.query = Query
