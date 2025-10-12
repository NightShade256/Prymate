from .console import main_helper

__version__ = "0.6.0"
__author__ = "Anish Jewalikar"
__license__ = "MIT"
__all__ = ["main"]


def main(source_file: str | None = None):
    main_helper(__version__, source_file)
