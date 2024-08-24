"""
Module contains the main function for the CLI interface of the package
"""

from . import moods
from .version import VERSION


def main() -> None:
    """
    Main function for the CLI interface of the package
    Prints a formatted CLI string with the version and a randomly colored mood
    """

    cli_string = moods.generate_cli_string(VERSION)
    print(cli_string)


if __name__ == "__main__":
    main()
