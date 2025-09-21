#!/usr/bin/env python3
import sys
from config import load_or_create_config
from db_utils import DatabaseTable
from display_code import Display, TerminalDisplay, GraphicDisplay
import asyncio
import threading
import time

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
    

async def main():
    db_table = DatabaseTable(DB_PATH)
    disp = TerminalDisplay(db_table)

    def display_loop():
        while True:
            try:
                asyncio.run(disp.update())
            except Exception as e:
                print(f"Chyba při aktualizaci displaye: {e}")
            time.sleep(10)

    threading.Thread(target=display_loop, daemon=True).start()

    if len(sys.argv) > 1:
        if sys.argv[1] == "cli":
            import cli_control_code
            await cli_control_code.main(db_table)
        elif sys.argv[1] == "tele":
            import telegram_bot_code
            await telegram_bot_code.main(db_table, TOKEN, ALLOWED_CHAT_IDS)
        else:
            acknowledge_wrong_parameter()
    else:
        acknowledge_wrong_parameter()

if __name__ == "__main__":
    asyncio.run(main())