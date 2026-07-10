"""
Retro Game Launcher verzióinformációk.

Verzióemeléskor csak az APP_VERSION értékét kell módosítani.
A .deb build, az APT repo workflow, az AppStream metainfo,
a Névjegy ablak és a dokumentációs verzió ebből az egy értékből dolgozik.
"""

APP_VERSION = "0.2.14"

BUILD_DEB_YML_VERSION = APP_VERSION
PUBLISH_APT_REPO_YML_VERSION = APP_VERSION

APPSTREAM_RELEASE_VERSION = APP_VERSION
ABOUT_DIALOG_VERSION = APP_VERSION
MAIN_DOC_VERSION = APP_VERSION
