import os

TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "")
WEBHOOK_HOST: str = os.getenv("DETA_SPACE_APP_HOSTNAME", "")
SERVICE_ACCOUNT_FILE_PATH: str = os.getenv("SERVICE_ACCOUNT_FILE_PATH", "")

WELCOME_MD_FILE_PATH: str = os.getenv("WELCOME_MD_FILE_PATH", "")
HELP_MD_FILE_PATH: str = os.getenv("HELP_MD_FILE_PATH", "")
