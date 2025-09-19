import threading
import time
from datetime import datetime

# je potrba nejak vyresit tohle, aby probihala aktualizace
#napada me - vyrobit tridu display, instance se vytvori v main a bude predavat dal 
# jednotlivym botum, aby moh
def update_display_loop():
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Aktuální čas: {now}")
        time.sleep(1)


# ddstane radky primo z databaze
async def update_display(summary):
    display_to_terminal(summary)


def display_to_terminal(summary):
    def get_fill_spaces(total_len, content, padding):
        return " " * (total_len + padding - len(str(content)))
    max_len = [0,0,0]
    for line in summary:
        for i in range(0,3):
            if len(str(line[i])) > max_len[i]:
                max_len[i] = len(str(line[i]))
    pad = 2
    print("=== Aktualizace displeje ===")
    for line in summary:
        print(f"{line[0]}{get_fill_spaces(max_len[0], line[0], pad)}{line[1]}{get_fill_spaces(max_len[1], line[1], pad)}{line[2]}")
    print("============================")


