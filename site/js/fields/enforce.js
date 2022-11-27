export default {
	phone: function(field)
	{
		field.value = field.value.replace(/[^0-9]/g, '')
	},

	id: function(field)
	{
		field.value = field.value.replace(/[ \t\n\r]/g, '')
	},
}
