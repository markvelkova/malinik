#!/usr/bin/env python3
import sys
from config import load_or_create_config

config = load_or_create_config()
DB_PATH = config["db_path"]
TOKEN = config["bot_token"]
ALLOWED_CHAT_IDS = set(config["allowed_chat_ids"])
TOPIC = config["topic"]

# momentalne - zadny parametr -> telegram bot, parametr cli -> cli bot

def acknowledge_wrong_parameter():
    print("Neplatný parametr, vyberte si z:\n" \
            "'cli' pro ovládání z terminálu\n" \
            "'tele' pro ovládání z Telegramu\n"\
            "pak použijte ./main.py parametr")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "cli":
            import cli_control_code
            cli_control_code.main(DB_PATH)
        elif sys.argv[1] == "tele":
            import telegram_bot_code
            telegram_bot_code.main(DB_PATH, TOKEN, ALLOWED_CHAT_IDS)
        else:
            acknowledge_wrong_parameter()
    else:
        acknowledge_wrong_parameter()
        
if __name__ == "__main__":
    main()
