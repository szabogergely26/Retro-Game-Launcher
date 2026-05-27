# Retro Game Launcher
# Státusz: korai, működő prototipus !

Egyszerű, PySide6 alapú Linuxos segédprogram retro játékok indítóikonjainak létrehozásához.

A projekt célja hosszabb távon egy könnyen használható, kártyás felületű retro játék launcher készítése, ahol a felvett játékok ikonokkal/képekkel jelennek meg, és kattintásra közvetlenül indíthatók.

## Jelenlegi állapot

A projekt jelenleg korai prototípus állapotban van.

A most működő funkciók:

- PySide6 alapú grafikus ablak
- játék nevének megadása
- indítófájl kiválasztása
- ikonfájl kiválasztása
- indítási típus kiválasztása:
  - Natív / közvetlen indítás
  - DOSBox
  - Wine
  - Egyedi parancs
- `.desktop` fájl létrehozása a felhasználói alkalmazásmenübe
- KDE menü frissítése `kbuildsycoca6` / `kbuildsycoca5` segítségével

A generált indítófájl helye:

```text
~/.local/share/applications/
```

## Követelmények
Python 3
PySide6
Linux asztali környezet
DOSBox, ha DOS-os játékot szeretnél indítani


## Virtuális környezet telepítése
1. python3 -m venv .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt


## Futtatás
source .venv/bin/activate
python main.py



## Használat
- Add meg a játék nevét.
- Válaszd ki az indítófájlt.
- Válassz ikonfájlt.
- Válaszd ki az indítás típusát.
- Kattints az Indító létrehozása gombra.
- Szükség esetén kattints a Menü frissítése gombra.

KDE alatt a létrehozott indító a menüben a Játékok kategóriában jelenhet meg.


# Jelenlegi projekt-struktúra
Retro-Game-Launcher/
├── apps/
│   ├── core/
│   │   └── desktop_writer.py
│   ├── resources/
│   └── ui/
│       ├── launcher_form.py
│       └── main_window.py
├── main.py
├── requirements.txt
└── README.md



# Fejlesztési terv

## Következő tervezett lépések:


- főablak átalakítása játékkártyás nézetté
- kártyára kattintva játék indítása
- később hover effektek és sötét téma



# Cél

A cél nem egy teljes Lutris-klón, hanem egy egyszerű, átlátható, saját használatra kényelmes retro játék indító.



## Következő lépések

- .desktop újragenerálása módosítás után


## Későbbi ötletek

- Storage/fstab ellenőrzés
- Ikonkezelés szépítése
- Játék kategória integráció
- Egyszerűbb Lutris-szerű nézet

