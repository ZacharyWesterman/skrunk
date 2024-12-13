__all__ = ['schema']

import ariadne
from graphql import GraphQLField, GraphQLNonNull, GraphQLList, GraphQLScalarType, GraphQLObjectType, GraphQLUnionType, GraphQLArgument
from functools import cache


def trim_type(data_type) -> GraphQLScalarType | GraphQLObjectType:
	_tp = data_type
	while True:
		if isinstance(_tp, GraphQLNonNull) or isinstance(_tp, GraphQLList):
			_tp = _tp.of_type
		else:
			break
	return _tp


def print_type_fields(fields: dict, indent: str) -> str:
	text = ''

	for i in fields:
		text += f'{indent}{i}'

		field_type = trim_type(fields[i].type)
		if isinstance(field_type, GraphQLObjectType):
			text += ' {\n'
			text += print_type_fields(field_type.fields, f'\t{indent}')
			text += f'{indent}}}'

		text += '\n'

	return text


def print_field(field_type: str, field_name: str, field: GraphQLField) -> str:
	text = ''

	return_type = trim_type(field.type)

	# Print parameter list
	if field.args:
		text += f'{field_type} (' + ', '.join([f'${k}: {field.args[k].type}' for k in field.args]) + ') {\n'
		text += f'\t{field_name} (' + ', '.join([f'{k}: ${k}' for k in field.args]) + ') '
	else:
		text += f'{field_type} {{ {field_name} '

	indent = '\t\t' if field.args else '\t'

	if isinstance(return_type, GraphQLUnionType):
		text += f'{{\n{indent}__typename\n'

		for i in return_type.types:
			text += f'{indent}...on {i} {{\n'
			if isinstance(i, GraphQLObjectType):
				text += print_type_fields(i.fields, indent + '\t')
			else:
				text += f'{i}'
			text += f'{indent}}}\n'

		text += f'{indent[0:-1]}}}'
		if field.args:
			text += '\n}'
		else:
			text += '}'

	elif isinstance(return_type, GraphQLObjectType):
		text += '{\n'

		text += print_type_fields(return_type.fields, indent)

		if field.args:
			text += '\t}\n}'
		else:
			text += '} }'
	else:
		if field.args:
			text += '\n}'
		else:
			text += '}'

	return text + '\n'


def get_type(type, param_type=None) -> dict:
	_tp = trim_type(type)
	fields = []

	if isinstance(_tp, GraphQLUnionType):
		fields = [str(i) for i in _tp.types]
	elif isinstance(_tp, GraphQLObjectType):
		fields = [str(i.type) for i in _tp.fields.values()]
	elif isinstance(_tp, GraphQLArgument):
		_tp = trim_type(_tp)

	if param_type:
		param_type = trim_type(param_type)
		if not isinstance(param_type, GraphQLScalarType):
			fields = [str(i.type) for i in param_type.fields.values()]

	return {
		'name': str(_tp),
		'type': trim_type(param_type) if param_type else str(_tp),
		'union': isinstance(_tp, GraphQLUnionType),
		'subtypes': fields,
	}


def get_meta_types(data_type) -> tuple[bool, bool]:
	optional = True
	array = False

	_tp = data_type
	while True:
		if isinstance(_tp, GraphQLNonNull):
			_tp = _tp.of_type
			optional = False
		if isinstance(_tp, GraphQLList):
			array = True
			_tp = _tp.of_type
		else:
			break

	return optional, array


@cache
def schema():
	"""Cache the schema since it will never change until the server restarts"""

	type_defs = ariadne.load_schema_from_path('application/schema')
	schema = ariadne.make_executable_schema(type_defs)

	queries = schema.query_type.fields
	mutations = schema.mutation_type.fields

	output_data = {
		'mutations': [],
		'queries': [],
		'types': [],
	}

	data_types = {}

	def build_types(items: dict[str, GraphQLField]) -> None:
		for i in items:
			if str(i).startswith('_SRV_DUMMY'):
				continue
			field: GraphQLField = items[i]

			retn_type = get_type(field.type)
			data_types[retn_type['type']] = retn_type

			for f in field.args:
				param_type = get_type(field.args[f], field.args[f].type)
				data_types[param_type['type']] = param_type

	def generate(kind: str, altkind: str, items: dict[str, GraphQLField]) -> None:
		for i in items:
			if i[0] == '_':
				continue
			field: GraphQLField = items[i]

			return_type = data_types[str(trim_type(field.type))]
			return_type['optional'], return_type['array'] = get_meta_types(field.type)

			output_data[kind] += [{
				'name': i,
				'params': [],
				'query': print_field(altkind, i, field),
				'returns': return_type,
			}]

	build_types(queries)
	build_types(mutations)
	output_data['types'] = data_types.values()

	generate('queries', 'query', queries)
	generate('mutations', 'mutation', mutations)

	return output_data
