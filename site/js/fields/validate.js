export default {
	phone: function(field)
	{
		$.enforce.phone(field)

		if (field.value.length === 0)
			field.value = field.defaultValue

		if (field.value.length != 10) {
			field.classList.add('error')
			return false
		} else {
			field.classList.remove('error')
			return true
		}
	},

	number: function(field)
	{
		if (field.validity.valid)
			field.classList.remove('error')
		else
			field.classList.add('error')

		return field.validity.valid
	},
}
