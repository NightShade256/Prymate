# Prymate

A simple interpreter for the [Monkey](https://monkeylang.org/) programming language written in Python.

## Usage

> [!NOTE]
> You need to have `uv` installed as a prerequisite.

To enter the REPL environment, invoke Prymate without any arguments:

```bash
$ uv run prymate

Prymate 0.5.0 [running on Linux]
Type exit() to leave the REPL.

>>> puts("Hello, world!")
Hello, world!
null
```

Or, you can alternatively execute a file by specifying the file path through `-f` or `--file` argument:

```bash
$ uv run prymate -f [path to file]

...
```

Tests can also be run using `uv`:

```bash
$ uv run pytest

...
```

## Features

Prymate implements all vanilla Monkey constructs, and also implements following additional features:

1. Additional Inbuilt Functions like `help`, `exit`, `type`, `gets`, `sumarr`, `zip`, `int`, `str` and more
2. String `!=` and `==` operations
3. Modulo `%` for determining the remainder of a expression `a / b`
4. Floating point literals (type `FLOAT` in the interpreter)
5. Variable mutability
6. While Loops
7. Constants

## Resources

This interpreter wouldn't have been possible without the excellent `Writing an Interpreter in Go` by `Thorsten Ball`.
I highly recommend you to read it, and build your own Monkey interpreter!

## License

Prymate is licensed under the terms of the MIT license.
