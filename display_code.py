import threading
import time
from datetime import datetime
from abc import ABC, abstractmethod
from datetime import datetime
import db_utils

class Display(ABC):
    @abstractmethod
    def __init__(self, database):
        self.database = database        
        self.time = datetime.now() 
    async def update(self):
        pass


class TerminalDisplay(Display):
    async def update(self):
        self.time = datetime.now()
        display_to_terminal(self.database.get_whole_database())
    


class GraphicDisplay(Display):
    async def update(self, data):
        print(f"Grafika zobrazuje: {data}")

# ddstane radky primo z databaze

def display_to_terminal(data):
    def get_fill_spaces(total_len, content, padding):
        return " " * (total_len + padding - len(str(content)))
    
    max_len = [0,0,0]
    for line in data:
        for i in range(0,3):
            if len(str(line[i])) > max_len[i]:
                max_len[i] = len(str(line[i]))
    pad = 2
    print("=== Aktualizace displeje ===")
    for line in data:
        print(f"{line[0]}{get_fill_spaces(max_len[0], line[0], pad)}{line[1]}{get_fill_spaces(max_len[1], line[1], pad)}{line[2]}")
    print("============================")



