#!/usr/bin/env python3
import sys
from config import load_or_create_config

config = load_or_create_config()
DB_PATH = config["db_path"]
TOKEN = config["bot_token"]
ALLOWED_CHAT_IDS = set(config["allowed_chat_ids"])
TOPIC = config["topic"]

# mmentane - zadny parametr -> telegram bot, parametr cli -> cli bot

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        import cli_control_code
        cli_control_code.main(DB_PATH)
    else:
        import telegram_bot_code
        telegram_bot_code.main(DB_PATH, TOKEN, ALLOWED_CHAT_IDS)

if __name__ == "__main__":
    main()
