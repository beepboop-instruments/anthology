

# Package imports
from textual.app import ComposeResult
from textual.widgets import Static

# Module imports
from ...journals.book import Author
from ..widgets.entry import EntryList

class AuthorEntry(Static):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]
    
    def compose(self) -> ComposeResult:
        yield EntryList(title="Author", params=list(Author.entry_params().values()))