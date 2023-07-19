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
term = g.regex(r'"(?:\\"|[^\"])+"', name='TERM')
regx = g.regex(r'r/((?![*+?])(?:[^\r\n\[/\\]|\\.|\[(?:[^\r\n\]\\]|\\.)*\])+)/', name='REGEX')


def symbol_handler(ast_node):
    ast_node.type = 'SYM'
    return ast_node


symbol = g.variant(regx, term, word, handler=symbol_handler)


def handle_group(ast_node):
    print(f'handle_group Before: {ast_node}')
    ast_node.data = [ast_node.data[0]] + [sub_group.data[1] for sub_group in ast_node.data[1].data]
    print(f'handle_group After: {ast_node}')
    return ast_node


group_delimiter = g.const('|')
group = g.group(
    symbol,
    g.repeat(g.group(group_delimiter, symbol)),
    handler=handle_group)


group.try_parse(TextIterator('x | y | z\n | a | b c d e'))

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
