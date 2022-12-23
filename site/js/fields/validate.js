export default {
	phone: value => value.length === 10,
	number: value => value.match(/^\d+(\.\d+)$/) !== null,
}
