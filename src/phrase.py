from src.finances import Spending

SPEDING_SCHEMA = Spending.generate_string_schema()

with open("src/static/bot_phrases/welcome.md", "r") as welcome_file:
    WELCOME_MESSAGE = welcome_file.read()

with open("src/static/bot_phrases/help.md", "r") as help_file:
    HELP_MESSAGE = help_file.read()
