export default {
	phone: value => value.replace(/[^0-9]/g, ''),
	id: value => value.replace(/[ \t\n\r]/g, '').toLowerCase(),
	tag: value => value.toLowerCase().trim(),
}
