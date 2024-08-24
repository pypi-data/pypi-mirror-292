import typer
from rich import print
from . import ExpressionParser, tree_analysis, Gene, distribute_rules

app = typer.Typer()


@app.command()
def run(rule:str):
    print(f"Rule:{rule}")
    print(ExpressionParser)
    parser = ExpressionParser()
    tokens = parser.tokenize(rule)
    print(tokens)
    tree = parser.parse(rule)
    print(tree)

if __name__=="__main__":
    app()
