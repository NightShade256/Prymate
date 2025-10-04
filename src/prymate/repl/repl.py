import platform

import prymate
from prymate.evaluator import evaluate
from prymate.lexer import Lexer
from prymate.objects import Environment
from prymate.parser import Parser

__all__ = ["start"]


def start() -> None:

    # Print some information.
    sys_env = platform.system()
    print(f"\nPrymate {prymate.__version__} [Running on {sys_env}]")
    print("Type exit() to exit from the REPL.\n")

    # Start the REPL loop.
    env = Environment()
    while True:
        line = input(">>> ")
        if not line:
            continue

        parser = Parser(Lexer(line))
        program = parser.parse_program()

        if parser.errors:
            print("There was a error while parsing the program.\nErrors:")
            for x in parser.errors:
                print(f"\t{x}\n")
            continue

        evaluated = evaluate(program, env)
        if evaluated is not None:
            print(evaluated.inspect())
