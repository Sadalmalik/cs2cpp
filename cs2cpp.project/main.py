from GrammarParser import *


def main():
    p = GrammarParser()
    lang = p.group(p.const("using"), p.regex(r'\w+'), p.const("."), p.regex(r'\w+'), p.const(";"))
    iterator = TextIterator('using System.Reflection;')
    result, _ = lang.try_parse(iterator)
    print(result)


if __name__ == '__main__':
    main()
