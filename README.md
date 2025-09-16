# Maliník - (nejen) RaspberryPi připomínkovník
Jednoduchá aplikace umožňující přes Telegram bota interagovat s SQLite databází a zobrazuje aktuální stav databáze.

**MOMENTÁLNĚ JEN VYPISUJE PŘÍMO NA STROJI BĚHU OBSAH, KTERÝ POTOM PŘIJDE NA KONKRÉTNÍ DISPLAY**
## Před spuštěním
### Na RaspberryPi (případně jiném místě běhu programu)
Předpokládá se spouštění na RaspberryPi, tedy následující pokyny jsou uplatnitelné pouze na Linuxu
```
git clone https://github.com/markvelkova/malinik.git
```
- stáhne odtud potřebné soubory do samostatné složky
```
sudo apt update && sudo apt install -y python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install python-telegram-bot[asyncio] aiosqlite
```
- nainstaluje virtuální prostředí pro python, spustí ho a do něj stáhne potřebné knihovny
```
chmod +x <cesta_k_souboru_bot_code.py>
```
- nastaví hlavní soubor jako spustitelný
### V Telegramu
- otevřít chat s uživatelem @BotFather
- příkazem `/newbot` vyrobit nového bota (BotFather vás provede procesem)
- zkopírovat si bot TOKEN pro pozdější použití
## Spuštění
Pokud není aktivované vitruální prosřtedí, pak ho výše uvedeným příkazem aktivujte, pak je možno spustit program
```
./bot_code.py
```
Pokud se spouští poprvé, bude chtít cestu k databází (pokud nevyplníte, vytvoří si ji sám), token k botovi (viz [zde](###v-telegramu), a chat_id (je možno ignorovat a doplnit později). Všechny tyto údaje se uloží do souboru `config.json`, kde je možné je upravit, vzorový soubor je k nahlédnutí v `config.example.json`.

## Komunikace s botem
Je třeba otevřít chat s botem v Telegramu (odkaz získáte z komunikace s BotFather), po spuštění programu se příkazem `/start` vypíše nápověda. 

## Výstup
Momentálně se vše jen vypisuje na stroji, kde program běží, TODO: připravit pro konkrétní display.
