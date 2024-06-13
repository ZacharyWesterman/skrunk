export default {
	phone: value => value.length === 10,
	number: value => value.match(/^[-+]?\d+(\.\d+)?$/) !== null,
	integer: value => value.match(/^\d+/) !== null,
	email: value => value.match(
		/^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/) !== null,
}
