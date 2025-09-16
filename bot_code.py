#!/usr/bin/env python3
import os
import json
import asyncio
import display_code
from datetime import datetime
from typing import List

from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
import aiosqlite 
# asynchronni sqlite databaze


# KONFIGURACE
# -------------------------
CONFIG_FILE = "config.json"

def load_or_create_config():
    # pokud existuje ve složce soubor názvu v proměnné CONFIG_FILE výše, pak se použije
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        print("Vítej v Maliníku, je třeba vše nastavit, aby to fungovalo, jak bylo přislíbeno...\n Následující údaje můžete kdykoli upravit ručně v souboru config.json\n Pokud už jste tyto údaje někdy nastavovali a teď to nefunguje, zkontrolujte, zda soubor {CONFIG_FILE} existuje a je na správném místě")
        db_path = input("Zadej cestu k databázi (např. databaze.db): ").strip()
        token = input("Zadej Telegram bot token (získáš při tvorbě bota): ").strip()
        chat_ids = input("Zadej povolená chat_id oddělené čárkou (získáš od bota zavoláním příkazu /id, je možno doplnit ručně později):\n").strip()
        config = {
            "db_path": db_path or "malinik_db.db",
            "bot_token": token,
            "allowed_chat_ids": [int(chat_id.strip()) for chat_id in chat_ids.split(",") if chat_id.strip()]
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        print(f"Konfigurace byla úspěšně uložena uložena do {CONFIG_FILE}")
        return config

config = load_or_create_config()

DB_PATH = config["db_path"]
TOKEN = config["bot_token"]
ALLOWED_CHAT_IDS = set(config["allowed_chat_ids"])

# INICIALIZACE DATABAZE
# -----------------------------

# zalozi novou tabulku v databazi
# radek je id chat_id text_pripominky cas_vytvoreni
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)
        await db.commit()

# vlozi do databaze novy radek
async def add_reminder(chat_id: int, text: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO reminders (chat_id, text, created_at) VALUES (?, ?, ?)",
            (chat_id, text, datetime.utcnow().isoformat())
        )
        await db.commit()
    await send_to_display_and_update()

# vrati list zaznamu od chat_id
async def list_reminders_for(chat_id: int) -> List[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, text, created_at FROM reminders WHERE chat_id = ? ORDER BY id DESC",
            (chat_id,)
        )
        rows = await cur.fetchall()
    return [{"id": r[0], "text": r[1], "created_at": r[2]} for r in rows]

# vrati vsechny zaznamy
async def list_all_reminders() -> List[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, chat_id, text, created_at FROM reminders ORDER BY id DESC",
        )
        rows = await cur.fetchall()
    return [{"id": r[0], "chat_id": r[1], "text": r[2], "created_at": r[3]} for r in rows]

# smaze zaznam
async def remove_reminder(rid: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "DELETE FROM reminders WHERE id = ?",
            (rid,)
        )
        await db.commit()
        deleted = cur.rowcount
    if deleted:
        await send_to_display_and_update()
    return bool(deleted)

# OVLADANI DISPLAY
# ma ho na starost vedlejsi soubor display_code.py, ktery je nahore naimportovany, tady se jen predaji informace a zavola tamni funce
# -------------------------
async def send_to_display_and_update():
    async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT id, text FROM reminders ORDER BY id DESC LIMIT 10")
            rows = await cur.fetchall()
            summary = "\n".join(f"{r[0]}: {r[1]}" for r in rows)
    await display_code.update_display(summary)



# HANDELRY
# -------------------------

# aby se neuselo vzdy kontrolova, jestli je to spravne chat_id, mam na to tady funckci, ktera v pripade neuspechu nepusti dal
# funkce pod @allowed_only se povedou jako delegaty touto funkci
def allowed_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        if chat_id not in ALLOWED_CHAT_IDS:
            await update.message.reply_text("Nemáš oprávnění používat tohoto bota, pokud oprávnění chceš, použij příkaz /id a pošli své id správci, aby ho přidal do seznamu povolených id")
            return
        return await func(update, context)
    return wrapper

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ahoj!"
        "Můžeš používat tyto příkazy:\n/add <text> pro přidání\n/listmy pro zobrazení tvých záznamů\n/list pro zobrazení všech záznamů\n/remove <id> pro smazání"
        "Pošli /id pokud chceš zjistit své chat_id (užitečné, pokud nemáš přístup a brání se to tady)"
    )

# /id - vypíše chat_id
async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Tvoje chat_id je: {chat_id}")

# /add text - přidá text daný jako parametr jako připomínku
@allowed_only
async def add_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Použití: /add text připomínky")
        return
    await add_reminder(update.effective_chat.id, text)
    await update.message.reply_text(f"Přidáno: {text}")

# /list - vypíše uživateli do chatu všechny připomínky v databázi
@allowed_only
async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = await list_all_reminders()
    if not items:
        await update.message.reply_text("Žádné připomínky nejsou, pokud byly a ztratily se, kontaktuj správce, ať zkontroluje databázi.")
        return
    lines = [f"{it['id']}: {it['text']}" for it in items]
    await update.message.reply_text("\n".join(lines))

# /listmy - vypíše uživateli všechny jím přidané připomínky v databázi - mohlo by se hodit
@allowed_only
async def listmy_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = await list_reminders_for(update.effective_chat.id)
    if not items:
        await update.message.reply_text("Nemáš v databázi žádné své připomínky, nebyl záměr zobrazit připomínky všech příkazem /list?")
        return
    lines = [f"{it['id']}: {it['text']}" for it in items]
    await update.message.reply_text("\n".join(lines))

# /remove id - odstraní přiomínku ddaného id
@allowed_only
async def remove_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Použití: /remove <id připomínky (číslo)>")
        return
    try:
        rid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID musí být číslo.")
        return
    ok = await remove_reminder(rid)
    if ok:
        await update.message.reply_text(f"Smazáno: {rid}")
    else:
        await update.message.reply_text("Položka s tímto ID neexistuje.")

# spiš pro debug, cokoli, co neni prikaz (nezacina lomitkem) se prida jako zaznam, kdyby se to tim nejak moc zaplevelovalo, vypnu tu funkci
@allowed_only
async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    if txt.startswith("/"):
        return
    await add_reminder(update.effective_chat.id, txt)
    await update.message.reply_text(f"Přidáno (text): {txt}, pokud jste to nechtěli udělat, zavolejte /list, podívejte se, jaké id má ta nová připomínka a potom zavolejte /remove id")

# SPUŠTĚNÍ
# -------------------------

async def post_init(application):
    await application.bot.set_my_commands([
        BotCommand("start", "Úvod a nápověda"),
        BotCommand("id", "Zobrazí tvé chat_id"),
        BotCommand("add", "Přidat připomínku: /add <text>"),
        BotCommand("list", "Seznam všech připomínek"),
        BotCommand("listmy", "Seznam všech mnou přidaných připomínek"),
        BotCommand("remove", "Smazat připomínku podle ID: /remove <id>"),
    ])

def main():
    asyncio.run(init_db())
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    # registrace příkazů
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("id", id_cmd))
    app.add_handler(CommandHandler("add", add_cmd))
    app.add_handler(CommandHandler("list", list_cmd))
    app.add_handler(CommandHandler("listmy", listmy_cmd))
    app.add_handler(CommandHandler("remove", remove_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))

    print("Bot spuštěn, čekám na zprávy...")
    app.run_polling()

if __name__ == "__main__":
    main()
