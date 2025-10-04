import argparse

import prymate

__all__ = ["main"]


def main() -> None:
    # Create a CLI argument parser.
    aparser = argparse.ArgumentParser("Execute Monkey Language code.")
    aparser.add_argument(
        "-f",
        "--file",
        metavar="file",
        type=str,
        help="Path to the Monkey Language file.",
    )

    args = aparser.parse_args()

    if args.file is None:
        try:
            prymate.repl.start()
        except KeyboardInterrupt:
            return print("KeyboardInterrupt encountered. Quitting.")

    else:
        # Check if the file is a monkey lang file.
        if not str(args.file).endswith((".m", ".mon", ".mk")):
            return print("Unrecognized file type. Only use .m, .mk or .mon files.")

        try:
            with open(args.file) as fp:
                code = fp.read()
        except FileNotFoundError:
            return print(f"File {args.file} does not exist.")
        else:
            lexer = prymate.lexer.Lexer(str(code))
            parser = prymate.parser.Parser(lexer)

            program = parser.parse_program()
            if parser.errors:
                print("Prymate encountered errors while parsing the program.")
                print("Errors:\n")
                for error in parser.errors:
                    print(error)

                return

            environment = prymate.objects.Environment()
            try:
                obj = prymate.evaluator.evaluate(program, environment)
                if isinstance(obj, prymate.objects.Error):
                    print("Prymate encountered an error while evaluating the program.")
                    print(f"Error:\n{obj.message}")
            except KeyboardInterrupt:
                return print("KeyboardInterrupt encountered. Quitting.")


if __name__ == "__main__":
    main()
