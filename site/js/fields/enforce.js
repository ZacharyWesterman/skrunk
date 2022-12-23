export default {
	id: value => value.replace(/[^\w]/g, '').toLowerCase(),
	tag: value => value.toLowerCase(),
	phone: value => value.replace(/[^0-9]/g, ''),
}
