# ddstane radky primo z databaze
async def update_display(summary):
    print("=== Aktualizace displeje ===")
    for line in summary:
        print(f"{line[0]}: {line[1]}        {line[2]}")
    print("============================")
    # TODO: realne vypisovat