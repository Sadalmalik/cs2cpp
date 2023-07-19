# My Simple grammar parser
import re


class ASTNode:
    def __init__(self, _type, _data, **kwargs):
        self.type = _type
        self.data = _data
        if 'iterator' in kwargs:
            it: TextIterator = kwargs.get('iterator')
            self.line = it.line
            self.char = it.char
        else:
            self.line = kwargs.get('_line', 0)
            self.char = kwargs.get('_char', 0)

    def __str__(self):
        d = self.data
        if isinstance(d, list):
            d = ', '.join(str(i) for i in d)
        else:
            d = f"'{d}'"
        return f"[ {self.type}, {self.line}:{self.char}, {d} ]"


class TextIterator:
    def __init__(self, _text, _index=0, _line=0, _char=0):
        self.len = len(_text)
        self.text = _text
        self.index = _index
        self.line = _line
        self.char = _char

    def skip(self, symbols=' \t\r\n'):
        t_char = self.char
        t_line = self.line
        i = self.index
        while i < self.len and self.text[i] in symbols:
            t_char += 1
            if self.text[i] in '\r\n':
                t_line += 1
                t_char = 0
            i += 1
        return TextIterator(self.text, i, t_line, t_char)

    def next(self, size):
        next_index = self.index + size
        t_char = self.char
        t_line = self.line
        for i in range(self.index, next_index):
            t_char += 1
            if self.text[i] in '\r\n':
                t_line += 1
                t_char = 0
        return TextIterator(self.text, next_index, t_line, self.index)

    def __str__(self):
        return f"[iterator at {self.line}:{self.char} : '{self.text[self.index:10]}...']"


class GrammarParser:
    def __init__(self):
        self.skip_symbols = ['\n', '\r', '\t', ' ']
        self.nodes = []
        self.root = None

    def set_root(self, node):
        self.root = node

    def parse(self, text: str):
        if self.root is None:
            raise Exception("Grammar root not defined!")
        return self.root.try_parse(TextIterator(text))

    def const(self, term, **kwargs):
        return NodeConst(self, term, **kwargs)

    def regex(self, regex, **kwargs):
        return NodeRegex(self, regex, **kwargs)

    def group(self, *args, **kwargs):
        return NodeGroup(self, *args, **kwargs)

    def variant(self, *args, **kwargs):
        return NodeVariant(self, *args, **kwargs)

    def repeat(self, *args, **kwargs):
        return NodeRepeat(self, *args, **kwargs)

    def optional(self, node, **kwargs):
        return NodeOptional(self, node, **kwargs)


class NodeBase:
    def __init__(self, parser: GrammarParser, **kwargs):
        self.name = kwargs.get('name', 'Node')
        self.handler = kwargs.get('handler', None)
        self.parser = parser

    def handle(self, ast_node: ASTNode) -> ASTNode:
        if ast_node is None:
            return ast_node
        if self.handler is not None:
            return self.handler(ast_node)
        return ast_node

    def try_parse(self, iterator: TextIterator):
        return None, 0


class NodeConst(NodeBase):
    def __init__(self, parser: GrammarParser, term: str, **kwargs):
        super().__init__(parser, **kwargs)
        self.term = term
        self.size = len(term)

    def try_parse(self, iterator: TextIterator):
        iterator = iterator.skip()
        if self.term == iterator.text[iterator.index:iterator.index + self.size]:
            return self.handle(ASTNode('CONST', self.term, iterator=iterator)), iterator.next(self.size)
        return None, 0


class NodeRegex(NodeBase):
    def __init__(self, parser: GrammarParser, regex, **kwargs):
        super().__init__(parser, **kwargs)
        self.regex = regex

    def try_parse(self, iterator: TextIterator):
        iterator = iterator.skip()
        m = re.match(self.regex, iterator.text[iterator.index:])
        if m is not None:
            g = m.group(0)
            return self.handle(ASTNode('REGEX', g, iterator=iterator)), iterator.next(len(g))
        return None, 0


class NodeGroup(NodeBase):
    def __init__(self, parser: GrammarParser, *nodes, **kwargs):
        super().__init__(parser, **kwargs)
        self.nodes = nodes

    def try_parse(self, iterator: TextIterator):
        iterator = iterator.skip()
        result = []
        sub_iterator = iterator
        for node in self.nodes:
            val, sub_iterator = node.try_parse(sub_iterator)
            if val is None:
                return None, sub_iterator
            result.append(val)
        return self.handle(ASTNode('GROUP', result, iterator=iterator)), sub_iterator


class NodeVariant(NodeBase):
    def __init__(self, parser: GrammarParser, *nodes, **kwargs):
        super().__init__(parser, **kwargs)
        self.nodes = nodes

    def try_parse(self, iterator: TextIterator):
        iterator = iterator.skip()
        for node in self.nodes:
            val, sub_iterator = node.try_parse(iterator)
            if val is not None:
                return self.handle(val), sub_iterator
        return None, iterator


class NodeRepeat(NodeBase):
    def __init__(self, parser: GrammarParser, *args, **kwargs):
        super().__init__(parser, **kwargs)
        self.min = kwargs.get('min', 0)
        self.max = kwargs.get('max', -1)
        self.node = NodeGroup(*args) if len(args) > 1 else args[0]

    def try_parse(self, iterator: TextIterator):
        iterator = iterator.skip()
        sub_iterator = iterator
        counter = self.min
        result = []
        while True:
            if self.max != -1:
                counter += 1
                if counter >= self.max:
                    break
            val, sub_iterator = self.node.try_parse(sub_iterator)
            if val is None:
                break
            result.append(val)
        if len(result) == 0:
            return None, iterator
        return self.handle(ASTNode('REPEAT', result, iterator=iterator)), sub_iterator


class NodeOptional(NodeBase):
    def __init__(self, parser: GrammarParser, node, **kwargs):
        super().__init__(parser, **kwargs)
        self.node = node

    def try_parse(self, iterator: TextIterator):
        iterator = iterator.skip()
        val, sub_iterator = self.node.try_parse(iterator)
        return self.handle(ASTNode('OPTIONAL', val, iterator=iterator)), sub_iterator
