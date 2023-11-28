"""
Author Entry

A class for author infor input.

"""

# Package imports
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static
from typing import Any

# Module imports
from ...journals.book import Author, Book
from ..widgets.entry import EntryList

class AuthorEntry(Static):
    
    _db: Any
    
    def __init__(self, db:Any):
        self._db = db
        super().__init__(
            classes="entry-cols")
    
    def compose(self) -> ComposeResult:
        yield EntryList(
            title="Author",
            params=list(Author.entry_params().values()),
            selection=[(author, author) for author in Author.list_all(self._db)]
        )
        
class BookEntry(Static):
    
    _db: Any
    
    def __init__(self, db:Any):
        self._db = db
        super().__init__()
        
    def compose(self) -> ComposeResult:
        with Horizontal(classes="hor-border"):
            yield EntryList(
                title="Book",
                params=list(Book.entry_params().values()),
                selection=[(book, book) for book in Book.list_all(self._db)]
            )
            yield AuthorEntry(self._db)