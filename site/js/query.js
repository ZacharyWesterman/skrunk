const Imports = {
	weather: import('/js/query/weather.js'),
	users: import('/js/query/users.js'),
	blobs: import('/js/query/blobs.js'),
	bugs: import('/js/query/bugs.js'),
	books: import('/js/query/books.js'),
}

let Query = {
	require: async module =>
	{
		if (Query[module] === undefined)
		{
			await Imports[module]
		}
	}
}
for (const i in Imports)
{
	Imports[i].then(module => Query[i] = module.default)
}
window.query = Query
