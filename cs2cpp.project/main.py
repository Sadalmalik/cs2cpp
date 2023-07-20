from GrammarParser import *


def main():
    p = GrammarParser()
    lang = p.group(p.const("using"), p.regex(r'\w+'), p.const("."), p.regex(r'\w+'), p.const(";"))
    iterator = TextIterator('using System.Reflection;')
    result, _ = lang.try_parse(iterator)
    print(result)


def test():
    for i in range(100,200,10):
        LegsPos = i
        up = ((LegsPos + 100) / 100) * 100 - LegsPos
        print(f"UP: {up}")


if __name__ == '__main__':
    #main()
    test()
