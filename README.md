# Maliník - (nejen) RaspberryPi připomínkovník
Jednoduchá aplikace umožňující přes Telegram bota interagovat s SQLite databází a zobrazuje aktuální stav databáze.

**MOMENTÁLNĚ JEN VYPISUJE PŘÍMO NA STROJI BĚHU OBSAH, KTERÝ POTOM PŘIJDE NA KONKRÉTNÍ DISPLAY**

**pozor: blíží se změny v komunikaci**
- zachován zatím kvůli zpětné kompatibilitě bot_code.py, ale nebude tam věčně
- doporučujeme začít spouštět přes main.py (pokud se spustí bez parametru, nepoznáte změnu, s parametrem `cli` spustí terminálovou verzi)
- v plánu je přidat komunikaci přes webovou aplikaci, v configu přibyl jeden řádek - doporučujeme smazat soubor `config.json` a nebo ho předělat podle aktualního `config.example.json` 

# Pro admina
Adminem je míněna osoba, která spravuje a nastavuje stroj, na němž program běží (například Raspberry Pi). Dále je návod, jak nastavit vše potřebné, a co budou potřebovat uživatelé.
## Před prvním spuštěním
### Na RaspberryPi (případně jiném místě běhu programu)
Předpokládá se spouštění na RaspberryPi, tedy následující pokyny jsou uplatnitelné pouze na Linuxu
```
git clone https://github.com/markvelkova/malinik.git
```
- stáhne odtud potřebné soubory do samostatné složky `malinik`
```
sudo apt update && sudo apt install -y python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install python-telegram-bot[asyncio] aiosqlite
```
- nainstaluje virtuální prostředí pro python, spustí ho a do něj stáhne potřebné knihovny
```
chmod +x <cesta k souboru bot_code.py>
```
- nastaví hlavní soubor jako spustitelný
- je třeba doplnit správnou cestu (tedy pokud jsem ve složce `malinik`, pak stačí jen `./bot_code.py`
### V Telegramu
- otevřít chat s uživatelem @BotFather
- příkazem `/newbot` vyrobit nového bota (BotFather vás provede procesem)
- zkopírovat si **bot TOKEN** pro pozdější použití
- uložit si **odkaz na účet bota**, aby potom mohl být zaslán uživatelům
## Spuštění
Pokud není aktivované vitruální prostředí, pak ho výše uvedeným příkazem `source venv/bin/activate` aktivujte (pokud je prostředí aktivováno, zobrazuje se na začátku promptu (venv), pak je možno spustit program
```
./bot_code.py
```
Pokud se spouští poprvé, bude chtít cestu k databází (pokud nevyplníte, vytvoří si ji sám), token k botovi (viz [V Telegramu](###v-telegramu), a chat_id (je možno ignorovat a doplnit později). Všechny tyto údaje se uloží do souboru `config.json`, kde je možné je upravit, vzorový soubor je k nahlédnutí v `config.example.json`.

**Program musí být spuštěn, aby bot fungoval, pokud nereaguje, pak je nejspíš program vypnut.**

## Vypnutí
Lze vypnout stiskem `Ctrl+C`, nicméně předpokládá se nepřetržitý běh. Nicméně může se hodit při aktualizaci.

## Co budou chtít uživatelé
#### odkaz na účet bota
Získá se v komunikaci s BotFather, něco jako `t.me/nazevBota`.
#### přidat id do povolených
Bot je po zahájení komunikace vyzve, aby zjistili své chat_id píkazem `/id` a kontaktovali admina, je třeba přidat toto id do `config.json`

## Aktualizace
Aktuální verzi si kdykoli můžete stáhnout, pokud jste ve složce s programem (typicky `malinik`) příkazem
```
git pull
```
který stáhne nové aktualizace z této stránky. Je třeba program nejprve vypnout a pak znova zapnout.

# Pro uživatele
## Komunikace přes Telegram
Je třeba otevřít chat s botem v Telegramu (odkaz získá admin z komunikace s BotFather, vyžádejte si ho od něj), po spuštění programu se příkazem `/start` vypíše nápověda. 

# Výsledný výstup
Momentálně se vše jen vypisuje na stroji, kde program běží, TODO: připravit pro konkrétní display.
