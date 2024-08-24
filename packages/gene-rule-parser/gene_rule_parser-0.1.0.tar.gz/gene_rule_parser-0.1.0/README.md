# Gene Parser AST

A rule expression in genetics can be found like this relation of
AND+OR:

``` python
rule = '(9045_AT1 and (B0783 and B0088)) or (3705_AT1 or (91012_AT1 and 55304_AT1))'
```

This module enables a a parser that convert an string expression that
relates the genes in a object structure like this:

``` python
Or(
    left=And(left=Gene(name='9045_AT1'), right=And(left=Gene(name='B0783'), right=Gene(name='B0088'))),
    right=Or(
        left=Gene(name='3705_AT1'),
        right=And(left=Gene(name='91012_AT1'), right=Gene(name='55304_AT1'))
    )
)
```

To process this and obtain the representative value first is necessary
use the **parser** method and then call **tree_analysis**. This last
function reads recursively all the tree and obtain, given this rules,
the final value:

- or : sum([a,b])
- and : min([a,b])

And, for UNKNOWN value:

- Expression(UNKNOWN) :: mean([Expression(G_i)])

With this is possible to have the representative value for the gene
rule expression.

Take a look on the examples on the **tests** directory.


# How install this.

Call **poetry**

``` shell
poetry install
```

Run the tests:

Basic example:

``` shell
poetry run python tests/test_basic.py 
```

General Example:

``` shell
poetry run python tests/test_parser_general.py 
```

# Check then the parser.

Once installed you can check the for gene rule expressions using the
command **rule_parser**. 

``` shell
rule_parser "1321A and 123123B and (123123B or 32312C)"
```
