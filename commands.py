from db_utils import add_reminder, list_all_reminders, list_reminders_for, remove_reminder

# zde jsou wrappery nad tím, co se vždy provede, když se zavolá daný příkaz, ať už odkudkoli

async def add_reminder_cmd(user_id: int, text: str):
    await add_reminder(user_id, text)
    return f"Přidáno: {text}"

async def list_all_cmd():
    items = await list_all_reminders()
    if not items:
        return "Žádné připomínky nejsou."
    return "\n".join(f"{it['id']}: {it['text']}" for it in items)

async def list_my_cmd(user_id: int):
    items = await list_reminders_for(user_id)
    if not items:
        return "Nemáš žádné své připomínky."
    return "\n".join(f"{it['id']}: {it['text']}" for it in items)

async def remove_cmd(rid: int):
    ok, text = await remove_reminder(rid)
    if ok:
        return f"Smazáno: {rid} - {text}"
    return "Položka s tímto ID neexistuje."