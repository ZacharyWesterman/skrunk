#!/usr/bin/env python3

import ariadne
from graphql import GraphQLField, GraphQLNonNull, GraphQLList, GraphQLScalarType, GraphQLObjectType, GraphQLUnionType
import subprocess

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

	#Print parameter list
	if field.args:
		text += f'{field_type} (' + ', '.join([ f'${k}: {field.args[k].type}' for k in field.args]) + ') {\n'
		text += f'\t{field_name} (' + ', '.join([ f'{k}: ${k}' for k in field.args]) + ') '
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


def main():
	type_defs = ariadne.load_schema_from_path('application/schema')
	schema = ariadne.make_executable_schema(type_defs)

	queries = schema.query_type.fields
	mutations = schema.mutation_type.fields

	subprocess.run(['git', 'clone', 'git@github.com:ZacharyWesterman/skrunk_api.git'])

	for i in queries:
		if i[0] == '_': continue
		field: GraphQLField = queries[i]
		text = print_field('query', i, field)
		with open(f'skrunk_api/queries/{i}.txt', 'w') as fp:
			fp.write(text)

	for i in mutations:
		if i[0] == '_': continue
		field: GraphQLField = mutations[i]
		text = print_field('mutation', i, field)
		with open(f'skrunk_api/queries/{i}.txt', 'w') as fp:
			fp.write(text)

	subprocess.run(['git', 'add', '--all'], cwd = 'skrunk_api')
	subprocess.run(['git', 'commit', '-m', 'Automatic API query update'], cwd = 'skrunk_api')
	subprocess.run(['git', 'push'], cwd = 'skrunk_api')
	subprocess.run(['rm', '-rf', 'skrunk_api'])

if __name__ == '__main__':
	main()
