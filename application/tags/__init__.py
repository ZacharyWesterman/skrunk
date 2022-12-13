from . import lexer
from . import exceptions
from . import tokens

def debug_print(tokens, indent = 0):
	if type(tokens) is list:
		for i in tokens:
			debug_print(i, indent)
	else:
		print('  '*indent, tokens.__class__.__name__, tokens.text)
		debug_print(tokens.children, indent + 1)

def parse(expression: str) -> tokens.Token:
	prev_len = -1
	tokens = lexer.parse(expression)
	while len(tokens) > 1:
		pos = 0
		while pos < len(tokens):
			#only operate on tokens that haven't already been operated on
			if len(tokens[pos].children) == 0:
				tokens = tokens[pos].operate(tokens, pos)
			if len(tokens) != prev_len:
				break
			pos += 1

		#if this round of parsing did not condense the expression,
		#then some other syntax error happened.
		if prev_len == len(tokens):
			raise exceptions.SyntaxError

		prev_len = len(tokens)

	debug_print(tokens)
	return tokens[0]
