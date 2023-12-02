from src.finances import Spending

SPEDING_SCHEMA = Spending.generate_string_schema()

with open("src/static/bot_phrases/welcome.md", "r") as f:
    WELCOME_MESSAGE = f.read()

with open("src/static/bot_phrases/help.md", "r") as f:
    HELP_MESSAGE = f.read()
