from GrammarParser import GrammarParser, TextIterator

g = GrammarParser()
examples = r'''
    <root> : root of grammar
    <sep> : ' \s\t\r\n'
    const : r/\w+/
    regex : r/r/((?![*+?])(?:[^\r\n\[/\\]|\\.|\[(?:[^\r\n\]\\]|\\.)*\])+)//
    variant : a | b | c
    group : a b c
    repeat : [ element ]
    optional : { element }
'''

word = g.regex(r'\w+', name='WORD')
mark = g.regex(r'<\w+>', name='MARK')
term = g.regex(r'"(?:\\"|[^\"])+"', name='TERM')
regx = g.regex(r'r/((?![*+?])(?:[^\r\n\[/\\]|\\.|\[(?:[^\r\n\]\\]|\\.)*\])+)/', name='REGEX')


symbol = g.variant(regx, mark, term, word)


def handle_group(ast_node):
    ast_node.data = [ast_node.data[0]] + [sub_group.data[1] for sub_group in ast_node.data[1].data]
    return ast_node


variation_delimiter = g.const('|')
variation = g.group(
    symbol,
    g.repeat(g.group(variation_delimiter, symbol), min=1),
    handler=handle_group)


result, _ = variation.try_parse(TextIterator('x | <y> | z ;\n | a | b c d e'))
print(result)

# variation = g.group(term, g.repeat(g.group(g.const('|'), g.repeat())))
# symbol = g.variant(term, regx, variation)
# line = g.group(term, g.const(':'), g.repeat(symbol))
# grammar = g.repeat(line)
#
# result = grammar.try_parse(examples)
#
#
# self_grammar = r'''
#     term : r/\w+/
#     const : r/'\w+'/
#     regex : r/r/((?![*+?])(?:[^\r\n\[/\\]|\\.|\[(?:[^\r\n\]\\]|\\.)*\])+)//
#     variant : '['
# '''
#
# regex_regex = r'r/((?![*+?])(?:[^\r\n\[/\\]|\\.|\[(?:[^\r\n\]\\]|\\.)*\])+)/'
#
#
# class GrammarBuilder:
#     def __init__(self, grammar):
#         pass
#
#     def parse(self, text):
#         pass
