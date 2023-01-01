const Imports = {
	weather: import('/js/mutate/weather.js'),
	users: import('/js/mutate/users.js'),
	blobs: import('/js/mutate/blobs.js'),
	bugs: import('/js/mutate/bugs.js'),
}

let Mutate = {}
for (const i in Imports)
{
	const module = await Imports[i]
	Mutate[i] = module.default
}
window.mutate = Mutate
