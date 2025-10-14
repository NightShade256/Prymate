import argparse
import pathlib
import platform

from prymate.evaluator import evaluate
from prymate.objects import Environment, Error
from prymate.parser import Parser
from prymate.scanner import Scanner

__all__ = ["main_helper"]


def main_helper(version: str, source_file: str | None = None) -> None:
    "Entry point for the Prymate interpreter."

    if source_file is not None:
        execute_file(pathlib.Path(source_file))
        return

    parser = argparse.ArgumentParser(
        prog="prymate",
        description=(
            "Run Monkey Language code from a file or start the interactive Prymate REPL. "
            "If no file is provided, Prymate launches the REPL by default."
        ),
        epilog="Example: prymate -f examples/hello.mon",
    )

    parser.add_argument(
        "-f",
        "--file",
        metavar="FILE",
        type=str,
        help=(
            "Path to a Monkey Language source file (.m, .mk, or .mon). "
            "If omitted, the interactive REPL will be started."
        ),
    )

    args = parser.parse_args()

    if args.file is not None:
        execute_file(pathlib.Path(args.file))

    else:
        try:
            start_repl(version)
        except KeyboardInterrupt:
            return print("Keyboard Interrupt - stopping execution")


def execute_file(path: pathlib.Path):
    """Execute a Monkey Language source file."""

    if path.suffix not in {".m", ".mk", ".mon"}:
        print(f"Unsupported file type: {path.suffix or 'unknown'}")
        print("Use a file ending with .m, .mk or .mon.")
        return

    if not path.exists():
        print(f"File not found: {path}")

    try:
        source = path.read_text("utf-8")
    except Exception as e:
        print(f"Failed to read file {path}: {e}")
        return

    scanner = Scanner(source)
    parser = Parser(scanner)
    program = parser.parse_program()

    if parser.parser_errors:
        print("Prymate encountered errors while parsing:\n")

        for error in parser.parser_errors:
            print(f"\t- {error}")

        return

    env = Environment()

    try:
        result = evaluate(env, program)

        if isinstance(result, Error):
            print("Prymate encountered a runtime error:\n")
            print(f"\t- {result.message}")
    except KeyboardInterrupt:
        print("Keyboard Interrupt - stopping execution")


def start_repl(version: str) -> None:
    """Start the interactive Prymate REPL."""

    print(f"Prymate {version} [running on {platform.system()}]")
    print("Type exit() to leave the REPL and help() to discover inbuilt functions.")

    env = Environment()

    while True:
        try:
            line = input(">>> ")
        except EOFError:
            break

        if not line:
            continue

        scanner = Scanner(line)
        parser = Parser(scanner)
        parsed_line = parser.parse_program()

        if parser.parser_errors:
            print("Prymate encountered errors while parsing:\n")

            for error in parser.parser_errors:
                print(f"\t- {error}")

            continue

        evaluated = evaluate(env, parsed_line)

        if evaluated is not None:
            print(str(evaluated))
