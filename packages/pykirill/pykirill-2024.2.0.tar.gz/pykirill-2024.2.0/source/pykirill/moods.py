"""
Module for generating random moods and formatted output strings for the CLI and notebooks
"""

import random

MOODS: list[tuple[str, float]] = [
    ("bros.....", 0.05),
    ("WE'RE BACK", 0.2),
    ("WE'RE SO BACK", 0.3),
    ("WE'RE REALLY SO BACK", 0.2),
    ("IT'S OVER", 0.1),
    ("IT'S SO OVER", 0.1),
    ("IT'S SO OVER (real)", 0.05),
]


def generate_mood() -> str:
    """
    Generate a random mood from the MOODS list with respective probabilities and return it with a randomly colored ANSI escape sequence.

    Returns:
        The mood string wrapped in an ANSI escape sequence for color.
    """

    moods, probabilities = zip(*MOODS)
    random_mood = random.choices(moods, weights=probabilities)[0]

    # Generate RGB values directly
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    # Create ANSI escape sequence for the color
    colored_mood = f"\033[38;2;{r};{g};{b}m{random_mood}\033[0m"

    return colored_mood


def generate_cli_string(version: str) -> str:
    """
    Generate a CLI output string with a version and a randomly colored mood.

    Args:
        version: The version string to include in the output.

    Returns:
        The formatted CLI string with the version and colored mood.
    """

    mood = generate_mood()
    return f"🐗 pykirill {version} says: {mood}"


def generate_notebook_string() -> str:
    """
    Generate a notebook output string with a randomly colored mood.

    Returns:
        The formatted notebook string with the colored mood.
    """

    mood = generate_mood()
    return f"Before embarking on a journey, 🐗 pykirill foretells a {mood} mood..."
