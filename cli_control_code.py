import asyncio
from commands import add_reminder_cmd, list_all_cmd, list_my_cmd, remove_cmd
from db_utils import configure, init_db

def main(DB_PATH=None):
    configure(DB_PATH)
    asyncio.run(cli_loop())

async def cli_loop():
    await init_db()
    USER_ID = 9999
    print("Terminálový MaliníkBot běží a čeká na příkazy")
    while True:
        cmd = input("> ").strip().split(maxsplit=1)
        if not cmd:
            continue
        if cmd[0] in ("exit", "quit"):
            break
        elif cmd[0] == "help":
            print("Příkazy: add <text>, list, listmy, remove <id>, quit")
        elif cmd[0] == "add" and len(cmd) > 1:
            print(await add_reminder_cmd(USER_ID, cmd[1]))
        elif cmd[0] == "list":
            print(await list_all_cmd())
        elif cmd[0] == "listmy":
            print(await list_my_cmd(USER_ID))
        elif cmd[0] == "remove" and len(cmd) > 1:
            try:
                rid = int(cmd[1])
                print(await remove_cmd(rid))
            except ValueError:
                print("ID musí být číslo.")
        else:
            print("Neznámý příkaz. Použij 'help'.")
