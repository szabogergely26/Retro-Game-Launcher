"""
Retro Game Launcher verzióinformációk.

Verzióemeléskor ezt a fájlt kell módosítani.
FONTOS!: VERZIÓVÁLTOZÁSNÁL MINDEN VERZIÓSZÁMNAK EGYEZNIE KELL!!!

"""

APP_VERSION = "0.2.11"

BUILD_DEB_YML_VERSION = "0.2.11"
PUBLISH_APT_REPO_YML_VERSION = "0.2.11"

APPSTREAM_RELEASE_VERSION = "0.2.11"
ABOUT_DIALOG_VERSION = "0.2.11"
MAIN_DOC_VERSION = "0.2.11"


_EXPECTED_VERSION = APP_VERSION

_VERSION_FIELDS = {
    "BUILD_DEB_YML_VERSION": BUILD_DEB_YML_VERSION,
    "PUBLISH_APT_REPO_YML_VERSION": PUBLISH_APT_REPO_YML_VERSION,
    "APPSTREAM_RELEASE_VERSION": APPSTREAM_RELEASE_VERSION,
    "ABOUT_DIALOG_VERSION": ABOUT_DIALOG_VERSION,
    "MAIN_DOC_VERSION": MAIN_DOC_VERSION,
}

for field_name, field_value in _VERSION_FIELDS.items():
    if field_value != _EXPECTED_VERSION:
        raise RuntimeError(
            f"Verzióeltérés: {field_name}={field_value}, "
            f"várt érték: {_EXPECTED_VERSION}"
        )
