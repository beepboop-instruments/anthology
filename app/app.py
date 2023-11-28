"""
App

The main application class for the viewer.

"""

# Library imports
import sys
from argparse import ArgumentParser, Namespace
from textual import __version__ as textual_version  # pylint: disable=no-name-in-module
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, RichLog

import pytest

# Module imports
from .. import __version__
from ..utility.info import APP_TITLE, APP_NAME, APP_DESC
from ..tui.screens.entry_book import AuthorEntry, BookEntry
from ..journals.book import Author

from ..database.config import DBCfg
from icecream import ic
        
test_db = DBCfg("./db/test.db")

class AnthologyTUI(App[None]):
    """The main TUI application class."""

    # App title
    TITLE = APP_TITLE

    CSS_PATH = [
        "../tui/css/common.tcss"
        ]
    
    BINDINGS = [
        Binding("ctrl+q", "app.quit", "Quit"),
        ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield BookEntry(test_db)
        yield RichLog()
        yield Footer()

def get_args() -> Namespace:
    """Parse and return the command line arguments.

    Returns:
        The result of parsing the arguments.
    """

    # Create the parser object.
    parser = ArgumentParser(
        prog=APP_NAME,
        description=f"{APP_TITLE} -- {APP_DESC}",
        epilog=f"v{__version__}",
    )

    # Add --version
    parser.add_argument(
        "-v",
        "--version",
        help="Show version information.",
        action="version",
        version=f"%(prog)s {__version__} (Textual v{textual_version})",
    )

    # Add --test
    parser.add_argument(
        "-t",
        "--test",
        help="Run built-in tests.",
        action="store_true",
    )

    # Add --debug
    parser.add_argument(
        "-d",
        "--debug",
        help="Enable debug mode. Run built-in tests with prints.",
        action="store_true",
    )

    # Finally, parse the command line.
    return parser.parse_args()

def main(cl_args:Namespace) -> None:
    """Main app function."""
    
    # run test option
    if cl_args.test:
        sys.exit(pytest.main(["./anthology/test"]))
        
    # run tests with prints
    if cl_args.debug:
        sys.exit(pytest.main(["./anthology/test","-s"]))
    
    # run the TUI
    sys.exit(AnthologyTUI().run())


def run() -> None:
    """Run the application."""
    main(get_args())
    #MarkdownViewer(get_args()).run()
