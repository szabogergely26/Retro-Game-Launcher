#!/usr/bin/env bash
set -euo pipefail

# Mindig a projekt gyökeréből dolgozunk, akkor is,
# ha a scriptet a packaging mappából indítjuk.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# A Debian csomag neve. Ez marad kisbetűs, kötőjeles csomagnév.
PACKAGE_NAME="retro-game-launcher"

# Az alkalmazás modern AppStream / desktop azonosítója.
# Ezt használja a .desktop fájl neve, a metainfo fájl neve és az ikon neve is.
APP_ID="io.github.szabogergely26.RetroGameLauncher"

# Aktuális csomagverzió a control fájlhoz és az AppStream metainfo-hoz.
# FONTOS: ellenőrizd/igazítsd ezt az importot az apps/version_info.py tényleges tartalmához!
VERSION="$(python3 -c 'from apps.version_info import APP_VERSION; print(APP_VERSION)')"

# Ide épül fel a Debian csomag könyvtárszerkezete (belső staging mappa,
# ennek a neve nem kerül ki sehova, csak build közben létezik).
BUILD_DIR="build/${PACKAGE_NAME}_${VERSION}_all"

# A végleges kimeneti .deb fájl -- ez MINDIG fix nevű, verziószám nélkül,
# hogy a weboldali/APT letöltési linket soha ne kelljen módosítani.
OUTPUT_FILE="build/${PACKAGE_NAME}.deb"

echo "Projekt gyökér: $PROJECT_ROOT"
echo "Csomag neve: $PACKAGE_NAME"
echo "Verzió: $VERSION"
echo "Kimeneti fájl: $OUTPUT_FILE"

# Korábbi build törlése.
rm -rf build
mkdir -p "${BUILD_DIR}/DEBIAN"
mkdir -p "${BUILD_DIR}/usr/share/${PACKAGE_NAME}"
mkdir -p "${BUILD_DIR}/usr/bin"
mkdir -p "${BUILD_DIR}/usr/share/applications"
mkdir -p "${BUILD_DIR}/usr/share/icons/hicolor/256x256/apps"
mkdir -p "${BUILD_DIR}/usr/share/metainfo"

# Programfájlok bemásolása a csomag /usr/share alatti saját mappájába.
cp -r apps "${BUILD_DIR}/usr/share/${PACKAGE_NAME}/"
cp main.py "${BUILD_DIR}/usr/share/${PACKAGE_NAME}/"
cp requirements.txt "${BUILD_DIR}/usr/share/${PACKAGE_NAME}/"

# Debian control fájl bemásolása és verzió beállítása.
cp packaging/debian/control.template "${BUILD_DIR}/DEBIAN/control"
sed -i "s/^Version: .*/Version: ${VERSION}/" "${BUILD_DIR}/DEBIAN/control"

# .desktop indító bemásolása RDNS fájlnévvel.
cp "packaging/debian/${APP_ID}.desktop" \
  "${BUILD_DIR}/usr/share/applications/${APP_ID}.desktop"

# Parancssori wrapper bemásolása.
cp packaging/linux/retro-game-launcher \
  "${BUILD_DIR}/usr/bin/retro-game-launcher"

# Alkalmazásikon bemásolása RDNS néven.
cp packaging/icons/retro-game-launcher.png \
  "${BUILD_DIR}/usr/share/icons/hicolor/256x256/apps/${APP_ID}.png"

# AppStream metainfo bemásolása RDNS fájlnévvel és verzió beállítása.
cp "packaging/debian/${APP_ID}.metainfo.xml" \
  "${BUILD_DIR}/usr/share/metainfo/${APP_ID}.metainfo.xml"
sed -i "s/release version=\"[^\"]*\"/release version=\"${VERSION}\"/" \
  "${BUILD_DIR}/usr/share/metainfo/${APP_ID}.metainfo.xml"

# Jogosultságok beállítása.
chmod 755 "${BUILD_DIR}/usr/bin/retro-game-launcher"
chmod 755 "${BUILD_DIR}/DEBIAN"
chmod 644 "${BUILD_DIR}/DEBIAN/control"
chmod 644 "${BUILD_DIR}/usr/share/applications/${APP_ID}.desktop"
chmod 644 "${BUILD_DIR}/usr/share/icons/hicolor/256x256/apps/${APP_ID}.png"
chmod 644 "${BUILD_DIR}/usr/share/metainfo/${APP_ID}.metainfo.xml"

# .deb csomag elkészítése -- explicit, fix kimeneti fájlnévvel.
dpkg-deb --build "${BUILD_DIR}" "${OUTPUT_FILE}"

echo
echo "Elkészült:"
echo "$OUTPUT_FILE"
