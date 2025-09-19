import os
import json

# KONFIGURACE
# -------------------------
CONFIG_FILE = "config.json"

def load_or_create_config():
    # pokud existuje ve složce soubor názvu v proměnné config_file, pak se použije
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        print("Vítej v Maliníku, je třeba vše nastavit, aby to fungovalo, jak bylo přislíbeno...\n Následující údaje můžete kdykoli upravit ručně v souboru config.json\n Pokud už jste tyto údaje někdy nastavovali a teď to nefunguje, zkontrolujte, zda soubor {CONFIG_FILE} existuje a je na správném místě")
        print("\nPOVINNNÉ ÚDAJE pro všechny způsoby komunikace:")
        db_path = input("Zadej cestu k databázi (např. databaze.db): ").strip()
        print("\nÚDAJE POTŘEBNÉ PRO TELEGRAM BOTA (pokud používáte jiný způsob, můžete ponechat prázdné):")
        token = input("Zadej Telegram bot token (získáš při tvorbě bota): ").strip()
        chat_ids = input("Zadej povolená chat_id oddělené čárkou (získáš od bota zavoláním příkazu /id, je možno doplnit ručně později):\n").strip()
        print("\nÚDAJE POTŘEBNÉ PRO KOMUNIKACI PŘES MOSQUITTO")
        topic = input("Zadej topic, na kterém bude program poslouchat: ").strip()
        config = {
            "db_path": db_path or "malinik_db.db",
            "bot_token": token,
            "allowed_chat_ids": [int(chat_id.strip()) for chat_id in chat_ids.split(",") if chat_id.strip()],
            "topic": topic
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        print(f"Konfigurace byla úspěšně uložena uložena do {CONFIG_FILE}")
        return config