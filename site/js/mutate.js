const Imports = {
	weather: import('/js/mutate/weather.js'),
	users: import('/js/mutate/users.js'),
	blobs: import('/js/mutate/blobs.js'),
	bugs: import('/js/mutate/bugs.js'),
	books: import('/js/mutate/books.js'),
}

let Mutate = {
	require: async module => {
		if (Mutate[module] === undefined) {
			await Imports[module]
		}
	}
}

for (const i in Imports) {
	Imports[i].then(module => Mutate[i] = module.default)
}
window.mutate = Mutate
