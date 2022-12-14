from . import exceptions
import re

INT = re.compile(r'^[0-9]+$')

class Token:
	def __init__(self, text: str):
		self.text = text
		self.children = []

	def operate(self, tokens: list, pos: int) -> list:
		return tokens

	def output(self):
		raise NotImplementedError(f'output() method is not implemented for {self.type()}.')

	def type(self):
		return self.__class__.__name__

	def coalesce(self) -> list:
		#fold together children for operators of the same type.
		kids = []
		for child in self.children:
			child.coalesce()
			if child.type() == 'Operator' and self.text == child.text:
				kids += child.children
			else:
				kids += [child]
		self.children = kids

class NoneToken(Token):
	def output(self) -> dict:
		return {}

class Operator(Token):
	def operate(self, tokens: list, pos: int) -> list:
		if pos == 0 or pos >= (len(tokens) - 1):
			raise exceptions.MissingOperand(self.text)

		ltype = tokens[pos-1].type()
		lkids = len(tokens[pos-1].children)

		rtype = tokens[pos+1].type()
		rkids = len(tokens[pos+1].children)

		#don't be greedy; let functions try to get their param if they can.
		if (rtype == 'Function' and rkids == 0) or ltype == 'RParen' or rtype == 'LParen':
			return tokens

		if (ltype != 'String' and lkids == 0) or (rtype != 'String' and rkids == 0):
			raise exceptions.MissingOperand(self.text)

		self.children = [ tokens[pos-1], tokens[pos+1] ]

		#fold together children for operators of the same type.
		self.coalesce()

		return tokens[0:pos-1] + [self] + tokens[pos+2::]

	def output(self) -> dict:
		return {
			f'${self.text}': [ i.output() for i in self.children ]
		}

class String(Token):
	def output(self) -> str:
		return { 'tags': self.text }

class LParen(Token):
	def operate(self, tokens: list, pos: int) -> list:
		if pos >= (len(tokens) - 2):
			raise exceptions.MissingRightParen

		ptype = tokens[pos+1].type()
		pkids = len(tokens[pos+1].children)

		rtype = tokens[pos+2].type()

		# inner expression hasn't been parsed yet, so exit early
		if rtype != 'RParen':
			return tokens

		if ptype != 'String' and pkids == 0:
			raise exceptions.EmptyParens

		#fold together children for operators of the same type.
		if ptype == 'Operator':
			tokens[pos+1].coalesce()

		return tokens[0:pos] + [tokens[pos+1]] + tokens[pos+3::]

class RParen(Token):
	pass

class Function(Token):
	def operate(self, tokens: list, pos: int) -> list:
		if pos >= (len(tokens) - 2):
			raise exceptions.MissingRightParen

		ptype = tokens[pos+1].type()
		pkids = len(tokens[pos+1].children)

		rtype = tokens[pos+2].type()
		rkids = len(tokens[pos+2].children)

		if ptype == 'RParen':
			raise exceptions.MissingParam(self.text)

		# inner expression hasn't been parsed yet, so exit early
		if rtype != 'RParen':
			return tokens

		if ptype != 'String' and pkids == 0:
			raise exceptions.MissingParam(self.text)

		#Currently, all functions require a precisely numeric param.
		if ptype != 'String' or not INT.match(tokens[pos+1].text):
			raise exceptions.BadFuncParam(f'The parameter given to "{self.text}" must be numeric.')

		self.children = [ tokens[pos+1] ]

		return tokens[0:pos] + [self] + tokens[pos+3::]

	def output(self) -> dict:
		if len(self.children) == 0:
			raise exceptions.MissingParam(self.text)

		#we know that the param will always be numeric, not an expression
		count = int(self.children[0].text)

		if self.text == 'eq':
			return { 'tags': { '$size': count } }
		elif self.text == 'lt':
			return { f'tags.{count-1}': { '$exists': False } }
		elif self.text == 'le':
			return { f'tags.{count}': { '$exists': False } }
		elif self.text == 'gt':
			return { f'tags.{count}': { '$exists': True } }
		elif self.text == 'ge':
			return { f'tags.{count-1}': { '$exists': True } }

		raise NotImplementedError(f'Output for function of type "{self.text}" is not implemented.')
