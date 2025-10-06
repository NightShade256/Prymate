import platform

import prymate
from prymate.evaluator import evaluate
from prymate.objects import Environment
from prymate.parser import Parser
from prymate.scanner import Scanner

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

        parser = Parser(Scanner(line))
        program = parser.parse_program()

        if parser.parser_errors:
            print("There was a error while parsing the program.\nErrors:")
            for x in parser.parser_errors:
                print(f"\t{x}\n")
            continue

        evaluated = evaluate(program, env)
        if evaluated is not None:
            print(evaluated.to_string())
