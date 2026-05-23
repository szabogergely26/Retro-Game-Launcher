# Retro Game Launcher

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
