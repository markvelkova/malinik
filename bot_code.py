#!/usr/bin/env python3
import os
import json
import asyncio

import display_code
import config
from db_utils import configure, init_db, add_reminder, list_reminders_for, list_all_reminders, remove_reminder

from datetime import datetime
from typing import List
from datetime import datetime, timezone

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

config = config.load_or_create_config() # volani funkce z config.py

DB_PATH = config["db_path"]
TOKEN = config["bot_token"]
ALLOWED_CHAT_IDS = set(config["allowed_chat_ids"])

configure(DB_PATH) #volani funkce z db_utils

# BOT HANDELRY
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
        "Můžeš používat tyto příkazy:\n"
        "/add <text> pro přidání\n"
        "/listmy pro zobrazení tvých záznamů\n"
        "/list pro zobrazení všech záznamů\n"
        "/remove <id> pro smazání\n"
        "/id na zjištění svého chat_id\n\n"
        "jiný text bude vyhodnocen jako připomínka a přidá se"
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
    ok, text = await remove_reminder(rid)
    if ok:
        await update.message.reply_text(f"Smazáno: {rid}- {text}")
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

    print("MaliníkBot spuštěn, čeká na zprávy...")
    app.run_polling()

if __name__ == "__main__":
    main()
