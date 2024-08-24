import re

from pykirill import moods


class TestGenerateMood:
    def test_generate_mood_output(self):
        mood = moods.generate_mood()
        assert isinstance(mood, str), "Output should be a string"

    def test_generate_mood_format(self):
        mood = moods.generate_mood()
        ansi_escape_pattern = r"\033\[38;2;\d+;\d+;\d+m.*\033\[0m"
        assert re.match(ansi_escape_pattern, mood), "Output should match ANSI escape sequence format"

    def test_generate_mood_content(self):
        mood = moods.generate_mood()
        mood_text = re.sub(r"\033\[.*?m", "", mood)
        assert mood_text.strip() in dict(moods.MOODS), "Mood should be one of the defined MOODS"


class TestGenerateCLIString:
    def test_generate_cli_string_output(self):
        version = "v1.0"
        cli_string = moods.generate_cli_string(version)
        assert isinstance(cli_string, str), "Output should be a string"

    def test_generate_cli_string_format(self):
        version = "v1.0"
        cli_string = moods.generate_cli_string(version)
        ansi_escape_pattern = r"\033\[38;2;\d+;\d+;\d+m.*\033\[0m"
        mood_part = re.search(ansi_escape_pattern, cli_string)
        assert mood_part is not None, "CLI string should contain an ANSI escape sequence"
        assert cli_string.startswith(
            f"🐗 pykirill {version} says: "
        ), "CLI string should start with the expected format"


class TestGenerateNotebookString:
    def test_generate_notebook_string_output(self):
        notebook_string = moods.generate_notebook_string()
        assert isinstance(notebook_string, str), "Output should be a string"

    def test_generate_notebook_string_format(self):
        notebook_string = moods.generate_notebook_string()
        ansi_escape_pattern = r"\033\[38;2;\d+;\d+;\d+m.*\033\[0m"
        mood_part = re.search(ansi_escape_pattern, notebook_string)
        assert mood_part is not None, "Notebook string should contain an ANSI escape sequence"
        assert notebook_string.startswith(
            "Before embarking on a journey, 🐗 pykirill foretells a "
        ), "Notebook string should start with the expected format"
