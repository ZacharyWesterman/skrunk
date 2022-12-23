export default {
	id: value => value.replace(/[^\w]/g, '').toLowerCase(),
	tag: value => value.toLowerCase().trim(),
	phone: value => value.replace(/[^0-9]/g, ''),
}
