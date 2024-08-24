try:
    from gen_lexer import lexer
except:
    from .gen_lexer import lexer
try:
    from gen_parser import parser, Expression, And, Or, Gene, Unknown
except: 
    from .gen_parser import parser, Expression, And, Or, Gene, Unknown

from dataclasses import dataclass
from functools import lru_cache
import polars as pl
import ply.yacc as yacc
import ply.lex as lex
from typing import List, Dict

@dataclass
class ExpressionParser:
    lexer: lex.Lexer = lexer
    parser: yacc.LRParser = parser

    def tokenize(self, data: str) -> list[lex.LexToken]:
        self.lexer.input(data)
        return list(iter(self.lexer.token, None))

    def parse(self, data: str) -> Expression:
        return self.parser.parse(data)



def distribute_rules(words: List[str], N: int) -> Dict[int, List[str]]:
    # Sort words by length
    sorted_words = sorted(words, key=len)
    
    # Initialize groups
    groups = {i: [] for i in range(N)}
    
    # Distribute words in a round-robin fashion
    for i, word in enumerate(sorted_words):
        group_index = i % N
        groups[group_index].append(word)
    
    return groups


def tree_analysis(
        tree:Expression, 
        df:pl.DataFrame):

    if isinstance(tree, Or):
        try:
            left_tree = tree.left
            right_tree = tree.right

            if not isinstance(left_tree,(Gene,Unknown)) and not isinstance(right_tree,(Gene,Unknown)):
                left = tree_analysis(
                        left_tree,
                        df)
                right = tree_analysis(
                        right_tree,
                        df)
                pair = [
                    left,
                    right
                ]
                return sum(pair)
            if isinstance(left_tree,(Gene,Unknown)) and not isinstance(right_tree,(Gene,Unknown)):

                valor_l = tree_analysis(
                    left_tree,
                    df)
                valor_r = tree_analysis(
                    right_tree,
                    df)
                return sum([valor_l, valor_r])
            if not isinstance(left_tree,(Gene,Unknown)) and isinstance(right_tree,(Gene,Unknown)):

                # just one value
                valor_r = tree_analysis(
                    right_tree,
                    df)
                valor_l = tree_analysis(
                    left_tree,
                    df)
                return sum([valor_l, valor_r])
            elif isinstance(left_tree,(Gene,Unknown)) and isinstance(right_tree,(Gene,Unknown)):
                # GENE OR GENE: sum(values) 
                a = tree_analysis(
                    left_tree,
                    df)
                b = tree_analysis(
                    right_tree,
                    df)
                return sum([a,b])

        except Exception as ex:
            raise ex

    elif isinstance(tree, And):
        left_tree = tree.left
        right_tree = tree.right
        if (
                isinstance(left_tree, (Gene, Unknown)) and 
                isinstance(right_tree, (Gene, Unknown))
        ):
            try:
                # GENE AND GENE: min(values)
                pair = [
                    tree_analysis(
                        left_tree,
                        df),
                    tree_analysis(
                        right_tree,
                        df)
                ]
                value = min(pair)
                return value
            except Exception as ex:
                raise ex

        elif (
                isinstance(left_tree, (Gene, Unknown)) and 
                isinstance(right_tree, (And, Or))
        ):
            try:
                valor_l = tree_analysis(
                    left_tree,
                    df)
                valor_r = tree_analysis(
                    right_tree,
                    df)
                return min([valor_l, valor_r])
            except Exception as ex:
                raise ex
            
        elif (
                isinstance(left_tree, (And, Or)) and 
                isinstance(right_tree, (Gene, Unknown))
        ):
            try:

                # just one value
                valor_r = tree_analysis(
                    right_tree,
                    df)
                valor_l = tree_analysis(
                    left_tree,
                    df)

                return min([valor_l, valor_r])
            except Exception as ex:
                raise ex
        elif (
                isinstance(left_tree, (And, Or)) and 
                isinstance(right_tree, (And, Or))
        ):
            try:
                pair = [
                    tree_analysis(
                        left_tree,
                        df), 
                    tree_analysis(
                        right_tree,
                        df)
                ]
                return min(pair)
            except Exception as ex:
                raise ex
    elif isinstance(tree, (Gene, Unknown)):
        # Case GENE or UNKNOWN
        pair = [tree.gen]

        filtered_df = df.filter(
            pl.col("Gene_ID").is_in(pair)
        )
        min_expression = filtered_df.select(
            pl.col("Expression").min()
        ).to_dict()["Expression"][0]
        return min_expression
    else:
        return 0
