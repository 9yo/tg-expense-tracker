from src.finances import Spending
from src.settings import HELP_MD_FILE_PATH, WELCOME_MD_FILE_PATH

SPEDING_SCHEMA = Spending.generate_string_schema()

with open(WELCOME_MD_FILE_PATH, "r") as welcome_file:
    WELCOME_MESSAGE = welcome_file.read()

with open(HELP_MD_FILE_PATH, "r") as help_file:
    HELP_MESSAGE = help_file.read()
