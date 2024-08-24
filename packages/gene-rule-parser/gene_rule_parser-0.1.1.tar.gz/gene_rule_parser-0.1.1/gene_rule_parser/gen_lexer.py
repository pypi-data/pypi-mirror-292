import ply.lex as lex
from typing import Any, Iterator, Union

# Define the list of token names
tokens: tuple[str, ...] = (
    'GENE',
    'AND',
    'OR',
    'LPAREN',
    'RPAREN',
    "UNKNOWN"
)

# Regular expression rules for simple tokens
t_AND: str = r'and'
t_OR: str = r'or'
t_LPAREN: str = r'\('
t_RPAREN: str = r'\)'
t_UNKNOWN: str = r'UNKNOWN'



# A regular expression rule with some action code
def t_GENE(t: lex.LexToken) -> lex.LexToken:
    r'(Y|Q|b|B|s|S|[0-9])([A-Z0-9]{1,9})?([CW])?(_[A-Z0-9]+)?(_AT[0-9])?'
    #r'([YQBSbyqs])?[A-Za-z0-9]{2,5}([CWcw])?'
    return t

# Define a rule so we can track line numbers
def t_newline(t: lex.LexToken) -> None:
    r'\n+'
    t.lexer.lineno += t.value.count('\n')

# A string containing ignored characters (spaces and tabs)
t_ignore: str = ' \t'

# Error handling rule
def t_error(t: lex.LexToken) -> None:
    print(f"Illegal character {t} -> '{t.value[0]}'")
    t.lexer.skip(1)
    raise 

# Build the lexer
lexer: lex.Lexer = lex.lex()
