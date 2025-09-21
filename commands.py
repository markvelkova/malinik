from db_utils import DatabaseTable

# zde jsou wrappery nad tím, co se vždy provede, když se zavolá daný příkaz, ať už odkudkoli

async def add_reminder_cmd(dbt, user_id: int, text: str):
    await dbt.add_reminder(user_id, text)
    return f"Přidáno: {text}"

async def list_all_cmd(dbt):
    items = await dbt.list_all_reminders()
    if not items:
        return "Žádné připomínky nejsou."
    return "\n".join(f"{it['id']}: {it['text']}" for it in items)

async def list_my_cmd(dbt, user_id: int):
    items = await dbt.list_reminders_for(user_id)
    if not items:
        return "Nemáš žádné své připomínky."
    return "\n".join(f"{it['id']}: {it['text']}" for it in items)

async def remove_cmd(dbt, rid: int):
    ok, text = await dbt.remove_reminder(rid)
    if ok:
        return f"Smazáno: {rid} - {text}"
    return "Položka s tímto ID neexistuje."