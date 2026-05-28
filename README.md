# Retro Game Launcher

**Státusz:** korai, működő prototípus

A Retro Game Launcher egy egyszerű, PySide6 alapú Linuxos alkalmazás retro játékok kezeléséhez és indításához.

A cél nem egy teljes Lutris-klón, hanem egy könnyen átlátható, saját használatra kényelmes launcher, amellyel DOSBox, Wine és natív Linux játékok vehetők fel egy helyi játéklistába, majd onnan közvetlenül indíthatók.

## Jelenlegi állapot

A projekt jelenleg korai, de már használható prototípus állapotban van.

A jelenleg működő fő funkciók:

- PySide6 alapú grafikus főablak
- felvett játékok táblázatos megjelenítése
- játék hozzáadása varázslóval
- játék neve, indítófájlja, ikonja és indítási típusa megadható
- támogatott indítási típusok:
  - natív Linux indítás
  - DOSBox
  - Wine
  - egyedi parancs előkészítve / későbbi bővítésre
- játék indítása a listából
- játék indítása dupla kattintással
- játék eltávolítása a launcher listából
- menübejegyzés és asztali ikon létrehozása
- létrehozott `.desktop` fájlok törlése játék eltávolításakor
- játéklista automatikus mentése helyi JSON fájlba
- játéklista automatikus betöltése induláskor
- `Fájl → Játéklista mentése...`
- `Fájl → Játéklista betöltése...`
- `Fájl → Játéklista törlése...`
- állapotsor játékdarabszámmal és méretadatokkal
- `Súgó → Névjegy`
- modulokra bontott főablak-kód

## Adattárolás

A launcher a felvett játékokat helyi JSON fájlban tárolja.

Alapértelmezett hely:

```text
~/.local/share/retro-game-launcher/games.json
```

A játéklista kézzel is menthető és visszatölthető a Fájl menüből. Ez újratelepítés vagy rendszerköltöztetés esetén hasznos.

Fontos: a játéklista mentése csak a launcher adatait menti, magukat a játékfájlokat nem. A visszatöltött lista akkor működik azonnal, ha a játékok ugyanazon az útvonalon elérhetők.

## Generált indítók

A létrehozott alkalmazásmenü-indítók helye:

```text
~/.local/share/applications/
```

Az asztali ikonok a felhasználó asztalára kerülnek, ha a játék hozzáadásakor ez be van jelölve.

## Követelmények

- Python 3
- PySide6
- Linux asztali környezet
- DOSBox DOS-os játékokhoz
- Wine Windowsos játékokhoz

## Virtuális környezet telepítése

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Futtatás fejlesztői módban

```bash
source .venv/bin/activate
python main.py
```

## Használat

1. Indítsd el az alkalmazást.
2. Kattints az **Új játék hozzáadása** gombra.
3. Add meg a játék nevét.
4. Válaszd ki az indítófájlt.
5. Válaszd ki az ikont, ha szükséges.
6. Válaszd ki az indítás típusát.
7. Döntsd el, készüljön-e menübejegyzés vagy asztali ikon.
8. A játék megjelenik a launcher listájában.
9. Az **Indítás** gombbal vagy dupla kattintással elindítható.

## Játéklista mentése és visszaállítása

A játéklista biztonsági mentéséhez:

```text
Fájl → Játéklista mentése...
```

Visszatöltéshez:

```text
Fájl → Játéklista betöltése...
```

A teljes játéklista törléséhez:

```text
Fájl → Játéklista törlése...
```

Ez csak a launcher listáját törli, a játékfájlokat nem.

## Jelenlegi projekt-struktúra

```text
Retro-Game-Launcher/
├── apps/
│   ├── core/
│   │   ├── desktop_writer.py
│   │   └── game_store.py
│   └── ui/
│       ├── add_game_wizard.py
│       ├── edit_game_dialog.py
│       ├── launcher_form.py
│       ├── main_window.py
│       └── main_window_parts/
│           ├── central_view.py
│           ├── game_actions.py
│           ├── game_helpers.py
│           ├── game_list.py
│           ├── menus.py
│           ├── statusbar.py
│           └── window_actions.py
├── main.py
├── requirements.txt
└── README.md
```

## Fejlesztési terv

Következő tervezett lépések:

- játék szerkesztési funkció visszahozása
- `.desktop` fájl újragenerálása játék módosítása után
- játékkártyás nézet kialakítása
- játékborítók / képek támogatása
- sötét téma
- beállítások ablak bővítése
- Wine-kompatibilitási beállítások
- DOSBox-profilok finomítása
- GitHub Actions alapú `.deb` csomaggenerálás
- később APT repós frissítési megoldás tesztelése

## Cél

A cél egy egyszerű, átlátható retro játék launcher Linuxra.

Első stabil cél:

```text
játék hozzáadása → lista mentése → indítás → biztonsági mentés / visszatöltés
```

Hosszabb távon:

```text
kártyás játékfelület → ikonok/képek → DOSBox/Wine profilok → csomagolt telepítés → frissíthető rendszer
```
