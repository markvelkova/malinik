import aiosqlite
from datetime import datetime, timezone
from typing import List, Tuple, Optional
from display_code import update_display

DB_PATH: str | None = None

def configure(db_path: str):
    """Nastaví cestu k DB pro všechny funkce"""
    global DB_PATH
    DB_PATH = db_path

# INICIALIZACE DATABAZE
# -----------------------------

# zalozi novou tabulku v databazi
# radek je id chat_id text_pripominky cas_vytvoreni
async def init_db():
    if not DB_PATH:
        raise RuntimeError("DB_PATH není nastaveno. Zavolejte configure() nejdříve.")
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
    if not DB_PATH:
        raise RuntimeError("DB_PATH není nastaveno. Zavolejte configure() nejdříve.")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO reminders (chat_id, text, created_at) VALUES (?, ?, ?)",
            (chat_id, text, datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
        )
        await db.commit()
    await send_to_display_and_update()

# vrati list zaznamu od chat_id
async def list_reminders_for(chat_id: int) -> List[dict]:
    if not DB_PATH:
        raise RuntimeError("DB_PATH není nastaveno. Zavolejte configure() nejdříve.")
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, text, created_at FROM reminders WHERE chat_id = ? ORDER BY id DESC",
            (chat_id,)
        )
        rows = await cur.fetchall()
    return [{"id": r[0], "text": r[1], "created_at": r[2]} for r in rows]

# vrati vsechny zaznamy
async def list_all_reminders() -> List[dict]:
    if not DB_PATH:
        raise RuntimeError("DB_PATH není nastaveno. Zavolejte configure() nejdříve.")
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, chat_id, text, created_at FROM reminders ORDER BY id DESC",
        )
        rows = await cur.fetchall()
    return [{"id": r[0], "chat_id": r[1], "text": r[2], "created_at": r[3]} for r in rows]

# smaze radek, a vrati text, ktery e smazal
async def remove_reminder(rid: int) -> tuple[bool, str | None]:
    if not DB_PATH:
        raise RuntimeError("DB_PATH není nastaveno. Zavolejte configure() nejdříve.")
    async with aiosqlite.connect(DB_PATH) as db:
        # vytahneme text pred smazanim
        cur = await db.execute(
            "SELECT text FROM reminders WHERE id = ?",
            (rid,)
        )
        row = await cur.fetchone()
        deleted_text = row[0] if row else None

        # smazeme
        cur = await db.execute(
            "DELETE FROM reminders WHERE id = ?",
            (rid,)
        )
        await db.commit()
        deleted = cur.rowcount

    if deleted:
        await send_to_display_and_update()

    return bool(deleted), deleted_text


# OVLADANI DISPLAY
# ma ho na starost vedlejsi soubor display_code.py, ktery je nahore naimportovany, tady se jen predaji informace a zavola tamni funce
# -------------------------
async def send_to_display_and_update():
    if not DB_PATH:
        raise RuntimeError("DB_PATH není nastaveno. Zavolejte configure() nejdříve.")
    async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT id, text, created_at FROM reminders ORDER BY id DESC LIMIT 10")
            rows = await cur.fetchall()
            #summary = "\n".join(f"{r[0]}: {r[1]}, {r[2]}" for r in rows)
    await update_display(rows)
