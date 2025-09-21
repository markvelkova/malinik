import aiosqlite
from datetime import datetime, timezone
from typing import List, Tuple, Optional
# from display_code import update_display
import aiosqlite
from datetime import datetime, timezone
from typing import List, Optional

class DatabaseTable:
    def __init__(self, db_path: str):
        """nastaví cestu k DB pro všechny funkce"""
        if not db_path:
            raise ValueError("db_path musí být zadán")
        self.DB_PATH = db_path

    # INICIALIZACE DATABAZE
    # -----------------------------
    async def init_db(self):
        """zalozi novou tabulku v databazi, radek je id chat_id text_pripominky cas_vytvoreni"""
        async with aiosqlite.connect(self.DB_PATH) as db:
            await db.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """)
            await db.commit()

    async def add_reminder(self, chat_id: int, text: str):
        """vlozi do databaze novy radek"""
        async with aiosqlite.connect(self.DB_PATH) as db:
            await db.execute(
                "INSERT INTO reminders (chat_id, text, created_at) VALUES (?, ?, ?)",
                (chat_id, text, datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
            )
            await db.commit()
        await self.send_to_display_and_update()

    async def list_reminders_for(self, chat_id: int) -> List[dict]:
        """vrati list zaznamu od chat_id"""
        async with aiosqlite.connect(self.DB_PATH) as db:
            cur = await db.execute(
                "SELECT id, text, created_at FROM reminders WHERE chat_id = ? ORDER BY id DESC",
                (chat_id,)
            )
            rows = await cur.fetchall()
        return [{"id": r[0], "text": r[1], "created_at": r[2]} for r in rows]

    async def list_all_reminders(self) -> List[dict]:
        """vrati vsechny zaznamy"""
        async with aiosqlite.connect(self.DB_PATH) as db:
            cur = await db.execute(
                "SELECT id, chat_id, text, created_at FROM reminders ORDER BY id DESC",
            )
            rows = await cur.fetchall()
        return [{"id": r[0], "chat_id": r[1], "text": r[2], "created_at": r[3]} for r in rows]

    async def remove_reminder(self, rid: int) -> tuple[bool, Optional[str]]:
        """smaze radek, a vrati text, ktery e smazal"""
        async with aiosqlite.connect(self.DB_PATH) as db:
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
            await self.send_to_display_and_update()

        return bool(deleted), deleted_text


    async def get_whole_database(self):
        """vratí všechny řádky a sloupce databáze"""
        async with await self._connect() as db:
            cur = await db.execute("SELECT * FROM reminders")
            rows = await cur.fetchall()
        return rows
    
    

    async def send_to_display_and_update(self):
        pass