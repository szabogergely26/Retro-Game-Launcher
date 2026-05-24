"""
Retro Game Launcher - .desktop fájl generálás

Ez a modul felel azért, hogy a megadott játékadatokból
Linuxon használható .desktop indítófájl készüljön.
"""

import os
import re
import unicodedata
from pathlib import Path


APPLICATIONS_DIR = Path.home() / ".local" / "share" / "applications"


def _slugify_name(name: str) -> str:
    """
    Biztonságos fájlnevet készít a játék nevéből.

    Példa:
    "Jazz Jackrabbit 2" -> "jazz-jackrabbit-2"
    """

    normalized = unicodedata.normalize("NFKD", name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_name = ascii_name.lower()
    ascii_name = re.sub(r"[^a-z0-9]+", "-", ascii_name)
    ascii_name = ascii_name.strip("-")

    return ascii_name or "retro-game"


def _quote_desktop_arg(value: str) -> str:
    """
    Idézőjelezés a .desktop Exec sorhoz.

    Azért kell, mert az útvonalakban lehet szóköz.
    """

    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def build_exec_command(executable_path: str, launcher_type: str) -> str:
    """
    Elkészíti az Exec sort a választott indítási típus alapján.
    """

    executable_path = executable_path.strip()
    launcher_type = launcher_type.strip().lower()

    if launcher_type == "dosbox":
        return f"dosbox {_quote_desktop_arg(executable_path)} -exit"

    if launcher_type == "wine":
        return f"wine {_quote_desktop_arg(executable_path)}"

    if launcher_type == "custom":
        return executable_path

    return _quote_desktop_arg(executable_path)



def create_menu_desktop_launcher(
    name: str,
    executable_path: str,
    icon_path: str,
    launcher_type: str,
) -> Path:

    """
    .desktop indító létrehozása a felhasználói alkalmazásmenübe.

    Cél:
    ~/.local/share/applications/<jatek-neve>.desktop
    """

    clean_name = name.strip()
    clean_executable = executable_path.strip()
    clean_icon = icon_path.strip()

    if not clean_name:
        raise ValueError("Hiányzik a játék neve.")

    if not clean_executable:
        raise ValueError("Hiányzik az indítófájl vagy parancs.")

    if launcher_type != "Egyedi parancs":
        executable = Path(clean_executable)

        if not executable.exists():
            raise FileNotFoundError(f"Az indítófájl nem található: {clean_executable}")

    if clean_icon:
        icon = Path(clean_icon)

        if not icon.exists():
            raise FileNotFoundError(f"Az ikonfájl nem található: {clean_icon}")

    APPLICATIONS_DIR.mkdir(parents=True, exist_ok=True)

    desktop_filename = f"{_slugify_name(clean_name)}.desktop"
    desktop_path = APPLICATIONS_DIR / desktop_filename

    exec_command = build_exec_command(clean_executable, launcher_type)

    desktop_lines = [
        "[Desktop Entry]",
        "Type=Application",
        f"Name={clean_name}",
        f"Exec={exec_command}",
        "Terminal=false",
        "Categories=Game;Emulator;",
        "NoDisplay=false",
        "StartupNotify=true",
        "X-KDE-SubstituteUID=false",
        "X-KDE-Username=",
    ]

    if clean_icon:
        desktop_lines.append(f"Icon={clean_icon}")

    desktop_content = "\n".join(desktop_lines) + "\n"

    desktop_path.write_text(desktop_content, encoding="utf-8")
    os.chmod(desktop_path, 0o755)

    return desktop_path





def create_desktop_icon_launcher(
    name: str,
    executable_path: str,
    icon_path: str,
    launcher_type: str,
) -> Path:
    """
    .desktop indító létrehozása a felhasználó Asztal mappájába.
    """

    desktop_dir = Path.home() / "Asztal"

    if not desktop_dir.exists():
        desktop_dir = Path.home() / "Desktop"

    desktop_dir.mkdir(parents=True, exist_ok=True)

    clean_name = name.strip()
    clean_icon = icon_path.strip()
    exec_command = build_exec_command(executable_path, launcher_type)

    desktop_filename = f"{_slugify_name(clean_name)}.desktop"
    desktop_path = desktop_dir / desktop_filename

    desktop_lines = [
        "[Desktop Entry]",
        "Type=Application",
        f"Name={clean_name}",
        f"Exec={exec_command}",
        "Terminal=false",
        "NoDisplay=false",
        "StartupNotify=true",
    ]

    if clean_icon:
        desktop_lines.append(f"Icon={clean_icon}")

    desktop_content = "\n".join(desktop_lines) + "\n"

    desktop_path.write_text(desktop_content, encoding="utf-8")
    os.chmod(desktop_path, 0o755)

    return desktop_path
