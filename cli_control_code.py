import asyncio
from commands import add_reminder_cmd, list_all_cmd, list_my_cmd, remove_cmd

class TerminalBot:
    def __init__(self, db_table):
        self.DB_TABLE = db_table

    async def start_in_loop(self):
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
                print(await add_reminder_cmd(self.DB_TABLE, USER_ID, cmd[1]))
            elif cmd[0] == "list":
                print(await list_all_cmd(self.DB_TABLE))
            elif cmd[0] == "listmy":
                print(await list_my_cmd(self.DB_TABLE, USER_ID))
            elif cmd[0] == "remove" and len(cmd) > 1:
                try:
                    rid = int(cmd[1])
                    print(await remove_cmd(self.DB_TABLE, rid))
                except ValueError:
                    print("ID musí být číslo.")
            else:
                print("Neznámý příkaz. Použij 'help'.")

def main(db_table):
    bot = TerminalBot(db_table)
    asyncio.run(bot.start_in_loop())
