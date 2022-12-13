class ParseError(Exception):
	pass

class SyntaxError(ParseError):
	def __init__(self):
		super().__init__(f'Syntax error.')

class UnterminatedString(ParseError):
	def __init__(self):
		super().__init__(f'Unterminated string.')

class InvalidSymbol(ParseError):
	def __init__(self, char: str):
		super().__init__(f'Unvalid symbol "{char}".')

class MissingOperand(ParseError):
	def __init__(self, oper: str):
		super().__init__(f'Missing operand for "{oper}" operator.')

class MissingParam(ParseError):
	def __init__(self, func: str):
		super().__init__(f'Missing parameter for "{func}" function.')

class EmptyParens(ParseError):
	def __init__(self):
		super().__init__('Parentheses must contain an expression.')

class MissingLeftParen(ParseError):
	def __init__(self):
		super().__init__('Missing left parenthesis "("')

class MissingRightParen(ParseError):
	def __init__(self):
		super().__init__('Missing right parenthesis ")"')

class BadFuncParam(ParseError):
	pass
