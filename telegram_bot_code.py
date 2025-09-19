# telegram_bot.py
import asyncio
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from db_utils import configure, init_db
from commands import add_reminder_cmd, list_all_cmd, list_my_cmd, remove_cmd

# nakonec bude trida telegramBOt
class TelegramBot:
    def __init__(self, DB_PATH, TOKEN, ALLOWED_CHAT_IDS):
        self.DB_PATH = DB_PATH
        self.TOKEN = TOKEN
        self.ALLOWED_CHAT_IDS = ALLOWED_CHAT_IDS
        configure(DB_PATH) # pripoji se k databazi, pripadne si ji zajisti

    # aby se neuselo vzdy kontrolova, jestli je to spravne chat_id, mam na to tady funckci, ktera v pripade neuspechu nepusti dal
    # funkce pod @allowed_only se povedou jako delegaty touto funkci
    def allowed_only(self, func):
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            chat_id = update.effective_chat.id
            if chat_id not in self.ALLOWED_CHAT_IDS:
                await update.message.reply_text(
                    "Nemáš oprávnění používat tohoto bota, pokud oprávnění chceš, použij /id a pošli své id správci."
                )
                return
            return await func(update, context)
        return wrapper

    # -------------------------
    # handlery
    async def start_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Ahoj!\n"
            "Příkazy:\n"
            "/add <text> - přidat připomínku\n"
            "/listmy - zobrazit své připomínky\n"
            "/list - zobrazit všechny připomínky\n"
            "/remove <id> - smazat připomínku\n"
            "/id - zjistit chat_id\n"
            "Jiný text se uloží jako připomínka."
        )

    async def id_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"Tvoje chat_id je: {update.effective_chat.id}")

    # /add text - přidá text daný jako parametr jako připomínku
    def add_cmd(self):
        @self.allowed_only
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            text = " ".join(context.args).strip()
            if not text:
                await update.message.reply_text("Použití: /add <text připomínky>")
                return
            await update.message.reply_text(await add_reminder_cmd(update.effective_chat.id, text))
        return handler

    # /list - vypíše uživateli do chatu všechny připomínky v databázi
    def list_cmd(self):
        @self.allowed_only
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(await list_all_cmd())
        return handler

    # /listmy - vypíše uživateli všechny jím přidané připomínky v databázi - mohlo by se hodit
    def listmy_cmd(self):
        @self.allowed_only
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(await list_my_cmd(update.effective_chat.id))
        return handler

    # /remove id - odstraní přiomínku ddaného id
    def remove_cmd_handler(self):
        @self.allowed_only
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if not context.args:
                await update.message.reply_text("Použití: /remove <id>")
                return
            try:
                rid = int(context.args[0])
            except ValueError:
                await update.message.reply_text("ID musí být číslo.")
                return
            await update.message.reply_text(await remove_cmd(rid))
        return handler

    # spiš pro debug, cokoli, co neni prikaz (nezacina lomitkem) se prida jako zaznam, kdyby se to tim nejak moc zaplevelovalo, vypnu tu funkci
    def text_message(self):
        @self.allowed_only
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            txt = update.message.text.strip()
            if txt.startswith("/"):
                return
            await update.message.reply_text(await add_reminder_cmd(update.effective_chat.id, txt))
        return handler

    # -------------------------
    #REISTRACE PRIKAZU
    def registrate_commands(self, app):
        app.add_handler(CommandHandler("start", self.start_cmd))
        app.add_handler(CommandHandler("id", self.id_cmd))
        app.add_handler(CommandHandler("add", self.add_cmd()))
        app.add_handler(CommandHandler("list", self.list_cmd()))
        app.add_handler(CommandHandler("listmy", self.listmy_cmd()))
        app.add_handler(CommandHandler("remove", self.remove_cmd_handler()))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_message()))

    #nastavení příkazů pro Telegram
    async def post_init(self, application):
        await application.bot.set_my_commands([
            BotCommand("start", "Úvod a nápověda"),
            BotCommand("id", "Zobrazí tvé chat_id"),
            BotCommand("add", "Přidat připomínku"),
            BotCommand("list", "Seznam všech připomínek"),
            BotCommand("listmy", "Seznam mnou přidaných připomínek"),
            BotCommand("remove", "Smazat připomínku podle ID"),
        ])

    # spuštění bota
    def start_bot(self):
        asyncio.run(init_db())
        app = ApplicationBuilder().token(self.TOKEN).post_init(self.post_init).build()
        self.registrate_commands(app)
        print("Telegram MaliníkBot spuštěn, čeká na zprávy...")
        app.run_polling()

# -------------------------
def main(DB_PATH, TOKEN, ALLOWED_CHAT_IDS):
    bot = TelegramBot(DB_PATH, TOKEN, ALLOWED_CHAT_IDS)
    bot.start_bot()

