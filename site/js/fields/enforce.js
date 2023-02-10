export default {
	id: value => value.replace(/[^\w]/g, '').toLowerCase(),
	tag: value => value.toLowerCase(),
	phone: value => value.replace(/[^0-9]/g, ''),
	hex: value => {
		const reduced = value.toLowerCase().replace(/[^0-9a-f]/g, '')
		return (reduced === '') ? '' : reduced.match(/.{1,2}/g).join(':')
	},
}
