__all__ = ['schema']

import ariadne
from graphql import GraphQLField, GraphQLNonNull, GraphQLList, GraphQLScalarType, GraphQLObjectType, GraphQLUnionType, GraphQLArgument
from functools import cache


def trim_type(data_type) -> GraphQLScalarType | GraphQLObjectType:
	"""
	Recursively trims a GraphQL type to its core type by removing any 
	GraphQLNonNull or GraphQLList wrappers.

	Args:
		data_type: The GraphQL type to be trimmed. It can be an instance of 
				   GraphQLNonNull, GraphQLList, GraphQLScalarType, or 
				   GraphQLObjectType.

	Returns:
		The core GraphQL type, which will be either a GraphQLScalarType or 
		GraphQLObjectType.
	"""
	_tp = data_type
	while True:
		if isinstance(_tp, GraphQLNonNull) or isinstance(_tp, GraphQLList):
			_tp = _tp.of_type
		else:
			break
	return _tp


def print_type_fields(fields: dict, indent: str) -> str:
	"""
	Recursively generates a string representation of GraphQL type fields with indentation.

	Args:
		fields (dict): A dictionary of GraphQL fields where keys are field names and values are field definitions.
		indent (str): A string used for indentation to format the output.

	Returns:
		str: A formatted string representing the GraphQL type fields with proper indentation.
	"""
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
	"""
	Generates a GraphQL query string for a given field.

	Args:
		field_type (str): The type of the field (e.g., query, mutation).
		field_name (str): The name of the field.
		field (GraphQLField): The GraphQL field object containing type and arguments.

	Returns:
		str: A formatted GraphQL query string for the specified field.
	"""
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
	"""
	Extracts and returns type information from a GraphQL type.

	Args:
		type: The GraphQL type to extract information from. This can be a GraphQLUnionType, GraphQLObjectType, or GraphQLArgument.
		param_type: An optional parameter that specifies the type of the parameter. This can be used to further refine the type information.

	Returns:
		dict: A dictionary containing the following keys:
			- 'name': The name of the type as a string.
			- 'type': The refined type if param_type is provided, otherwise the original type.
			- 'union': A boolean indicating whether the type is a GraphQLUnionType.
			- 'subtypes': A list of subtypes or fields associated with the type.
	"""
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
	"""
	Determines the metadata types of a given GraphQL data type.

	This function checks if the provided GraphQL data type is optional and/or an array.
	It traverses through the type to determine if it is wrapped in GraphQLNonNull or GraphQLList.

	Args:
		data_type: The GraphQL data type to be checked.

	Returns:
		A tuple containing two boolean values:
			- The first boolean indicates if the type is optional (True if optional, False if not).
			- The second boolean indicates if the type is an array (True if it is an array, False if not).
	"""
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
	"""
	Generates a GraphQL schema and extracts queries, mutations, and types.

	This function loads the GraphQL schema from the specified path, makes it executable,
	and then processes the queries and mutations to build a structured output containing
	the details of each query and mutation, including their parameters and return types.

	Returns:
		dict: A dictionary containing the following keys:
			- 'mutations': A list of mutation details.
			- 'queries': A list of query details.
			- 'types': A list of data types used in the schema.
	"""

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
