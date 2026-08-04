# Retro Game Launcher – jövőkép / fejlesztési backlog

Ez a dokumentum a Retro Game Launcher későbbi fejlesztési irányait gyűjti össze.
A cél egy egyszerűbb, átláthatóbb, saját igényekre szabott Lutris-szerű játékindító, amely kezeli a natív Linux, DOSBox és Wine játékokat, de nem telepít feleslegesen minden futtatókörnyezetet.

---

## 1. Alap filozófia

A Retro Game Launcher célja:

* egyszerű játéklista kezelése;
* natív Linux játékok indítása;
* DOSBox játékok kezelése;
* Windows/Wine játékok kezelése;
* saját, kipróbált játékprofilok használata;
* könnyű, átlátható felület;
* ne legyen túlkomplikált Lutris-klón;
* csak akkor telepítsen extra futtatókörnyezetet, amikor tényleg szükség van rá.

Fontos alapelv:

> Amit a program ismer, azt állítsa be automatikusan.
> Amit nem ismer, arra kérdezzen rá kulturáltan.

---

## 2. Futtatókörnyezetek

A játékokhoz tartozzon egy `runtime` mező.

Lehetséges értékek első körben:

* `native` – natív Linux játék
* `dosbox` – DOSBox játék
* `wine` – Windows / Wine játék

Később bővíthető:

* `proton`
* `scummvm`
* `emulator`

---

## 3. Új játék hozzáadása

Az „Új játék hozzáadása” funkció kerüljön be a **Fájl** menübe, és kapjon külön eszköztárgombot is.

### Fájl menü

```text
Fájl
├── Új játék hozzáadása...
├── Telepített Linux játékok keresése / frissítése
├── Importálás...
├── Exportálás...
├── Beállítások...
└── Kilépés
```

### Eszköztár

```text
[ Új játék ] [ Indítás ] [ Tulajdonságok ] [ Eltávolítás ] [ Beállítások ]
```

Az „Új játék hozzáadása” varázsló első lépése:

```text
Milyen játékot szeretnél hozzáadni?

[ Natív Linux játék ]
[ DOSBox játék ]
[ Windows / Wine játék ]
```

---

## 4. Igény szerinti futtatókörnyezet-telepítés

A program alaptelepítése legyen kicsi.

A `.deb` csomag ne telepítse automatikusan:

* Wine
* Lutris
* DOSBox
* DXVK
* winetricks
* egyéb nagy futtatókörnyezeteket

Csak a launcher saját működéséhez szükséges csomagok legyenek kötelező függőségek.

A futtatókörnyezeteket a program csak akkor kérje / telepítse, amikor szükség van rájuk.

### Példa

Ha a felhasználó DOSBox játékot ad hozzá:

```text
A DOSBox nincs telepítve.
Szükséges csomag:
- dosbox

[ Telepítés ] [ Parancs megjelenítése ] [ Mégse ]
```

Ha a felhasználó Wine játékot ad hozzá:

```text
A Wine futtatókörnyezet nincs teljesen előkészítve.

Hiányzó elemek:
- wine
- wine32
- winetricks
- cabextract

[ Telepítés ] [ Parancs megjelenítése ] [ Mégse ]
```

Fontos:

> Ha a felhasználó csak DOSBox játékokat akar, ne települjön fel a Wine-világ.

---

## 5. Natív Linux játékok automatikus felismerése

A program induláskor vagy külön frissítési művelettel keresse meg a telepített Linux játékokat.

Források:

```text
/usr/share/applications/
~/.local/share/applications/
```

A `.desktop` fájlokból kiolvasható:

* `Name`
* `Exec`
* `Icon`
* `Categories`
* `Comment`

A `Categories=Game;` kategóriájú alkalmazások automatikusan felvehetők natív Linux játékként.

### Mentett adatok

```text
name = SuperTuxKart
runtime = native
source = desktop_file
desktop_id = supertuxkart.desktop
exec = supertuxkart
icon = supertuxkart
auto_imported = true
```

Fontos:

* ne duplikáljon;
* ha egy korábban felismert játék eltűnik, ne törölje azonnal;
* inkább jelölje „nem található” állapotúként.

---

## 6. Wine támogatás

A Wine támogatás ne teljes Lutris-klón legyen, hanem saját, egyszerű profilrendszer.

### Alapelv

```text
Ismert játék → automatikus profil
Ismeretlen játék → kézi Wine-beállító varázsló
```

Ha ismert játékot adunk hozzá:

```text
Felismert játék:
Harry Potter és a Bölcsek köve

Ajánlott profil:
Windows XP / DirectX 9 / OpenGL DirectDraw

[ Profil alkalmazása ] [ Kézi beállítás ]
```

Ha ismeretlen:

```text
Ezt a játékot nem ismerem.
Szeretnél hozzá Wine-beállításokat megadni?

[ Igen ] [ Nem most ]
```

---

## 7. Wine QWizard

A Wine beállításokat ne közvetlenül `winecfg`-vel kezdje, hanem saját QWizard felülettel.

### Javasolt oldalak

```text
1. Futtatási mód / felismerés
2. Prefix
3. Kompatibilitási mód
4. DirectX / grafika
5. Komponensek
6. Indító EXE / telepítő
7. Összegzés és alkalmazás
```

### Prefix oldal

```text
Wine prefix

[ ] Új saját prefix létrehozása
[ ] Meglévő prefix használata
[ ] Gyűjtemény-prefix használata

Prefix neve:
[ gta-san-andreas ]

Architektúra:
[ 32 bites ] [ 64 bites ]
```

### Kompatibilitási mód

```text
Windows verzió:

[ Windows 95 ]
[ Windows 98 ]
[ Windows XP ]
[ Windows 7 ]
[ Windows 10 ]
```

### DirectX / grafika

```text
[ ] DirectX 9 DLL-ek
[ ] Régi DirectDraw / OpenGL renderer
[ ] DXVK használata
[ ] Virtuális asztal használata
```

### Komponensek

```text
[ ] DirectPlay
[ ] DirectInput
[ ] Visual C++ 6 runtime
[ ] Visual C++ 2005
[ ] Visual C++ 2008
[ ] Visual C++ 2010
[ ] Corefonts
[ ] MIDI támogatás régi játékokhoz
```

---

## 8. Haladó Wine mód

A varázsló alapból ne ijessze meg a felhasználót.

Legyen egy kapcsoló:

```text
[ ] Haladó beállítások megjelenítése
```

Ha be van kapcsolva, jelenjenek meg külön gombok:

```text
[ winecfg megnyitása ]
[ regedit megnyitása ]
[ winetricks kézi futtatása ]
[ Prefix mappa megnyitása ]
[ Terminál megnyitása ebben a prefixben ]
```

Fontos:

* ne nyisson meg mindent egyszerre;
* csak azt indítsa, amire a felhasználó rákattint.

---

## 9. Ismert Wine játékprofilok

A későbbi saját Wine-profil adatbázis tartalmazhatja:

* DCCD002 / Legjobb Win95 játékok CD
* Crysis 2007
* GTA III
* GTA San Andreas
* Harry Potter 1
* Harry Potter 3
* Harry Potter 5
* Need for Speed Underground 2

### Példa profil-logika

```text
DCCD002 Win95 gyűjtemény:
- közös win32 prefix
- Windows 95 mód
- DirectX 9 DLL-ek
- DirectPlay
- DirectInput
- vcrun6
```

Nagyobb játékokhoz inkább külön prefix:

```text
wine-prefixes/
├── crysis-2007/
├── gta-san-andreas/
├── harry-potter-1/
└── nfs-underground-2/
```

---

## 10. DOSBox támogatás

A DOSBox játékokhoz külön futtatólogika kell.

Lehetséges adatok:

```text
runtime = dosbox
game_path = ...
dosbox_config = ...
mount_path = ...
launch_command = ...
```

Első körben:

* DOS játék mappájának kiválasztása;
* indító `.exe`, `.com` vagy `.bat` kiválasztása;
* DOSBox config generálása;
* indítás egy kattintással.

Ha nincs DOSBox telepítve, csak a DOSBox csomagot kérje / telepítse.

---

## 11. Játéklista ikonok

A játéklistában minden játék kapjon ikont.

Ikonforrások sorrendje:

```text
1. Játék saját ikonja
2. Felhasználó által választott ikon
3. Runtime-alap ikon
4. Alapértelmezett fallback ikon
```

### Runtime ikonok

```text
Natív Linux  → Linux / alkalmazás ikon
DOSBox       → klasszikus DOS / monitor / floppy ikon
Wine         → Wine / Windows-játék ikon
```

DOSBoxhoz jó lenne egy klasszikus MS-DOS / pifmgr.dll hangulatú saját ikon.

Fontos:

* ne Microsoft ikonfájlt csomagoljunk;
* saját, hasonló hangulatú DOS ikont érdemes készíteni.

---

## 12. Kártyás és táblázatos nézet

A játéklista támogasson két fő megjelenítést:

```text
Beállítások
└── Megjelenés
    └── Játékfelület:
        [ Táblázat ]
        [ Kártya ]
```

### Táblázatos nézet

Jó sok játéknál, gyors kereséshez, technikai áttekintéshez.

Lehetséges oszlopok:

* ikon
* név
* futtatókörnyezet
* profil
* elérési út
* állapot

### Kártyás nézet

Látványosabb launcher-felület.

Kártyán megjelenhet:

* játék képe;
* játék neve;
* runtime ikon;
* runtime neve;
* profil / platform;
* indítás gomb;
* tulajdonságok gomb.

Példa:

```text
┌───────────────────────┐
│        [ KÉP ]        │
│ Crysis                │
│ Wine                  │
│ Windows játék         │
└───────────────────────┘
```

---

## 13. Játékképek

Minden játékhoz lehessen saját képet beállítani.

Támogatott formátumok:

* `.jpg`
* `.jpeg`
* `.png`
* `.bmp`
* később akár `.webp`

A „Tulajdonságok” ablakban legyen külön kép / ikon rész.

```text
Tulajdonságok
├── Általános
├── Futtatás
├── Kép / Ikon
└── Parancsikonok
```

A Kép / Ikon oldalon:

```text
Játék ikon:
[ Tallózás... ]

Kártyakép:
[ Tallózás... ]

[ Kép eltávolítása ]
[ Előnézet ]
```

Fontos különbség:

* kis ikon: lista / állapotsor / menü
* nagy kép: kártyás nézet

---

## 14. Szűrősáv

A főablakban legyen runtime-alapú szűrősáv.

Egyszerű forma:

```text
[ Minden ] [ Natív Linux ] [ DOSBox ] [ Wine ]
```

Később kombinálható szűrés:

```text
[x] DOSBox
[x] Wine
[ ] Natív Linux
```

Ez mutathatja csak a DOSBox + Wine játékokat.

Szűrési logika:

```text
ha Minden aktív:
    minden játék látszik
különben:
    csak azok, amelyek runtime értéke a kiválasztott listában van
```

---

## 15. Állapotsor

Az állapotsor mutassa a kijelölt játék fontos adatait.

Példa:

```text
12 játék | Kijelölve: GTA San Andreas | Futtatókörnyezet: Wine | Prefix: gta-san-andreas
```

DOSBox játék esetén:

```text
Kijelölve: Doom | Futtatókörnyezet: DOSBox | Config: doom.conf
```

Natív Linux játék esetén:

```text
Kijelölve: SuperTuxKart | Futtatókörnyezet: Natív Linux
```

Később ikonokkal:

```text
Kijelölve: GTA San Andreas | 🍷 Wine
```

---

## 16. Sötét téma

A launcher kapjon sötét témát.

Beállítások:

```text
Beállítások
└── Megjelenés
    ├── Téma:
    │   [ Rendszer témája ]
    │   [ Világos ]
    │   [ Sötét ]
    │
    └── Játékfelület:
        [ Táblázat ]
        [ Kártya ]
```

A sötét téma különösen jól illene a kártyás launcher-felülethez.

---

## 17. Hover-effekt

A kártyás nézet kapjon finom hover-effektet.

Cél:

* ne legyen harsány;
* ne villogjon;
* ne legyen túl webes/gameres;
* legyen elegáns, modern, de visszafogott.

Hover esetén:

* kártya enyhén kiemelkedik;
* finom árnyék;
* keret enyhén erősödik;
* kép enyhén hangsúlyosabb;
* opcionálisan megjelenhetnek gyorsgombok.

Példa:

```text
Normál:
[ kép ]
Crysis
Wine

Hover:
[ kép kiemelve ]
Crysis
Wine
[ Indítás ] [ Tulajdonságok ]
```

Ez a kártyás nézet „koronája”.

---

## 18. Tulajdonságok ablak

A játék tulajdonságai ablak később több oldalból állhat.

```text
Tulajdonságok
├── Általános
├── Futtatás
├── Wine / DOSBox beállítások
├── Kép / Ikon
└── Parancsikonok
```

### Általános

* játék neve;
* kategória;
* megjegyzés;
* runtime típusa.

### Futtatás

* indító parancs;
* munkakönyvtár;
* indítási paraméterek.

### Wine / DOSBox

Runtime szerint változó oldal.

Wine esetén:

* prefix;
* Windows verzió;
* profil;
* winecfg;
* regedit;
* winetricks;
* prefix mappa.

DOSBox esetén:

* DOSBox config;
* mount útvonal;
* indító fájl.

### Kép / Ikon

* kis ikon;
* kártyakép;
* előnézet.

### Parancsikonok

* asztali parancsikon létrehozása;
* alkalmazásmenü-parancsikon létrehozása;
* később alkalmazásmenü-parancsikon eltávolítása.

---

## 19. Fejlesztési sorrend – javaslat

### 1. UI alapok

* Új játék hozzáadása bekerül a Fájl menübe.
* Eszköztár létrehozása.
* Runtime mező előkészítése.
* Állapotsor runtime információval.

### 2. Megjelenítés

* Listaikonok.
* Runtime ikonok.
* Szűrősáv.
* Táblázat / kártya nézet választás.
* Kártyakép támogatás.
* Hover-effekt.

### 3. Natív Linux import

* `.desktop` fájlok beolvasása.
* `Categories=Game;` felismerése.
* Ikonok betöltése.
* Automatikus hozzáadás duplikáció nélkül.

### 4. DOSBox támogatás

* DOSBox runtime.
* DOSBox telepítés ellenőrzése.
* DOSBox játék hozzáadó varázsló.
* DOSBox config kezelés.

### 5. Wine támogatás

* Wine runtime.
* Wine függőségellenőrzés.
* Prefix kezelés.
* Ismert játékprofilok.
* Wine QWizard.
* Haladó Wine eszközök.

### 6. Profiladatbázis

* Saját Wine profilok JSON/adatbázis alapon.
* Ismert játékok automatikus felismerése.
* Ismeretlen játékok kézi beállítása.
* Sikeres kézi beállítás mentése saját profilként.

---

## 20. Végső cél

A Retro Game Launcher legyen egy egyszerűbb, saját igényekre szabott Lutris-szerű program.

Tudja:

* natív Linux játékok automatikus felismerését;
* DOSBox játékok kényelmes hozzáadását;
* Wine játékok profil alapú kezelését;
* futtatókörnyezetek igény szerinti telepítését;
* táblázatos és kártyás megjelenítést;
* játékikonokat és játékképeket;
* szűrősávot;
* sötét témát;
* finom hover-effektet;
* átlátható Tulajdonságok ablakot.

Ne legyen túlkomplikált, ne akarjon mindent tudni, de amit tud, azt kényelmesen, szépen és stabilan kezelje.

Alapelv:

> Egyszerűbb, saját Lutris.
> Átláthatóbb, kisebb, offline-barátabb.
> A saját játékokhoz és saját gépekhez igazítva.
