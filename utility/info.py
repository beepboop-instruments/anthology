"""
Info

Provides general info about the app.

"""

from typing_extensions import Final

from .. import __version__

# Name of the app
APP_NAME: Final[str] = "anthology"

# Title of the app
APP_TITLE: Final[str] = "Anthology"

# Full app name
APP_VERSION: Final[str] = f"{APP_TITLE} v{__version__}"

# Description of the app
APP_DESC: Final[str] = "A note taking and organization app."