import ply.yacc as yacc
from typing import Union, Tuple, Any, List
# Get the token map from the lexer. This is required.
try:
    from gen_lexer import tokens
except:
    from .gen_lexer import tokens

from dataclasses import dataclass
from typing import Union, List
from functools import lru_cache

@dataclass
class Expression:
    def group_and(self) -> List['Expression']:
        return [self]

@dataclass
class Gene(Expression):
    name: str

    @property
    def gen(self):
        return f"G_{self.name.upper()}"

@dataclass
class And(Expression):
    left: Expression
    right: Expression

    def group_and(self) -> List['Expression']:
        return self.left.group_and() + self.right.group_and()


@dataclass
class Or(Expression):
    left: Expression
    right: Expression

    def group_and(self) -> List['Expression']:
        return [self]


@dataclass
class Unknown(Expression):
    @property
    def gen(self):
        return f"G_UNKNOWN"

# Define the precedence rules
precedence: tuple[tuple[str, str], ...] = (
    ('left', 'OR'),
    ('left', 'AND'),
)

# Define the parsing rules
def p_expression_or(p: yacc.YaccProduction) -> None:
    'expression : expression OR expression'
    p[0] = Or(left=p[1], right=p[3])

def p_expression_and(p: yacc.YaccProduction) -> None:
    'expression : expression AND expression'
    p[0] = And(left=p[1], right=p[3])

def p_expression_group(p: yacc.YaccProduction) -> None:
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_gene(p: yacc.YaccProduction) -> None:
    'expression : GENE'
    p[0] = Gene(name=p[1])

def p_expression_unknown(p: yacc.YaccProduction) -> None:
    'expression : UNKNOWN'
    p[0] = Unknown()

def p_error(p: yacc.YaccProduction) -> None:
    print("Syntax error in input!")
    raise

# Build the parser
parser: yacc.LRParser = yacc.yacc()
