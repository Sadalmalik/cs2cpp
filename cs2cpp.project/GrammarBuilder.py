from GrammarParser import GrammarParser, TextIterator, ASTNode

g = GrammarParser()
examples = r'''
    <root> : expression
    <sep> : ' \s\t\r\n'
    const : r/\w+/
    regex : r/r/((?![*+?])(?:[^\r\n\[/\\]|\\.|\[(?:[^\r\n\]\\]|\\.)*\])+)//
    variant : a | b | c
    group : a b c
    repeat : [ expression ]
    optional : { expression }
    expression : ( element ) | optional | repeat | variant | group
'''

self_grammar = dict()

self_grammar['word'] = word = g.regex(r'\w+', name='word')
self_grammar['mark'] = mark = g.regex(r'<\w+>', name='mark')
self_grammar['term'] = term = g.regex(r'"(?:\\"|[^\"])+"', name='term')
self_grammar['regx'] = regx = g.regex(r'r/((?![*+?])(?:[^\r\n\[/\\]|\\.|\[(?:[^\r\n\]\\]|\\.)*\])+)/', name='regex')
self_grammar['symbol'] = symbol = g.variant(regx, mark, term, word)
self_grammar['variation'] = variation = g.group(symbol, g.repeat(g.group(g.const('|'), symbol), min=1))
self_grammar['grouping'] = grouping = g.group(symbol, g.repeat(symbol, min=1))
self_grammar['optional'] = optional = g.group(g.const('{'), ('require', 'expression'), g.const('}'))
self_grammar['repeat'] = repeat = g.group(g.const('['), ('require', 'expression'), g.const(']'))
self_grammar['expression'] = expression = g.variant(
    g.group(g.const('['), ('require', 'expression'), g.const(']')),
    optional, repeat, grouping)
self_grammar['line'] = line = g.group(g.variant(mark, word), g.const(':'), expression, g.const(';'))
self_grammar['<root>'] = root = g.repeat(line)


def handle_variation(ast_node):
    ast_node.data = [ast_node.data[0]] + [sub_group.data[1] for sub_group in ast_node.data[1].data]
    return ast_node


def handle_group(ast_node):
    ast_node.data = [ast_node.data[0]] + ast_node.data[1].data
    return ast_node


variation.add_handler(handle_variation)
grouping.add_handler(handle_group)


def walk_tree(ast_tree: ASTNode, handler):
    if handler is None:
        return
    for node in ast_tree.data:
        if isinstance(node, ASTNode):
            walk_tree(node, handler)
    handler(ast_tree)


def resolve_grammar(grammar):
    def handler(ast_node: ASTNode):
        if not isinstance(ast_node.data, list):
            return
        for i in range(len(ast_node.data)):
            if isinstance(ast_node.data[i], tuple):
                tag, name = ast_node.data[i]
                if tag == 'require':
                    ast_node.data[i] = grammar[name]
    for name, element in grammar.items():
        walk_tree(element, handler)


resolve_grammar(self_grammar)


"expression: ( expression ) | optional | repeat | variant | group"


expression = g.variant(
    g.group(g.const('('), ('require', 'expression'), g.const(')')),

)

optional.nodes[1] = expression



result, _ = variation.try_parse(TextIterator('x | <y> | z ;\n | a | b c d e'))
print(result)
result, _ = grouping.try_parse(TextIterator('a b c ; d e'))
print(result)
result, _ = optional.try_parse(TextIterator('{ x }'))
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
