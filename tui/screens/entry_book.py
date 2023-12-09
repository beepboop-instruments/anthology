"""
Author Entry

A class for author info input.

"""

# Package imports
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static
from typing import Any

# Module imports
from ...journals.book import Author, Book, BookAuthor
from ..widgets.entry import EntryForm, EntryList
from ..widgets.common import SaveButton, LabelInput

class AuthorEntry(Static):
    """A widget for entering author info."""
    
    _db: Any
    
    def __init__(self, db:Any):
        self._db = db
        super().__init__(
            classes="entry-cols")
    
    def compose(self) -> ComposeResult:
        yield EntryList(
            title="Author",
            params=list(Author.lut_aliases()),
            selection=[(author, author) for author in Author.list_all(self._db)]
        )

class BookEntry(Static):
    """A widget for entering book info."""
    
    _db: Any
    
    def __init__(self, db:Any):
        self._db = db
        super().__init__(
            classes="hor-border")
        
    def compose(self) -> ComposeResult:
        LabelInput(label="Title", id="Title")
        with Horizontal():
            yield EntryForm(
                title="Book",
                params=list(Book.lut_aliases()),
                pos=0
            )
            yield AuthorEntry(self._db)
        with Horizontal(classes="common--button-row"):
            yield SaveButton(id="save_book")

    def on_button_pressed(self, event: SaveButton.Pressed) -> None:
        if not event.button.id == "save_book":
            return
        # Get all the inputs present
        book_params = {}
        authors = []
        author_idx = 0
        for widget in self.query("Input"):
            # Parse the IDs for class names and parameters
            parsed_id = widget.id.split('_')
            in_type = parsed_id[0]
            in_param = parsed_id[1]
            in_idx = int(parsed_id[2])
            
            if in_type == "Book":
                book_params[in_param] = widget.value
            elif in_type == "Author":
                if in_param == "FirstName":
                    authors.append({})
                    author_idx += 1
                authors[author_idx-1][in_param] = widget.value
        
        new_book = Book(
            self._db,
            title=book_params["Title"],
            publisher=book_params["Publisher"],
            publishyear=book_params["PublishYear"],
            publishloc=book_params["PublishLocation"],
            edition=book_params["Edition"],
            numpages=int(book_params["NumberofPages"]),
            formattype=book_params["Format"],
            curpage=int(book_params["CurrentPage"]),
            timesread=int(book_params["TimesRead"]),
            rating=float(book_params["Rating"])
        )
        new_book.create()
        book_id = new_book.save()
        
        print(new_book, new_book.id)
        
        for author in authors:
            new_author = Author(
                self._db,
                firstname=author["FirstName"],
                midname=author["MiddleName"],
                lastname=author["LastName"],
                gender=author["Gender"],
                country=["Country"]
            )
            new_author.create()
            author["Author"] = new_author
            author["ID"] = new_author.save()
            BookAuthor(self._db).save((new_author.id, new_book.id))