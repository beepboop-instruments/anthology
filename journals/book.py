"""
Book

"""

# Library imports
from dataclasses import dataclass, Field

# Parent classes
from .medium   import *
from .utils    import oxford_comma_list

# --------------------------------------------------------------------
# Author Class -------------------------------------------------------

@dataclass
class Author(Creator):
    """The author class."""
    
    @property
    def book_ids(self) -> list[int]:
        """ Get list of the author's book IDs."""
        return BookAuthor.get_author_book_ids(self.id)

    @property
    def books(self) -> list[str]:
        """Get a list of the author's books."""
        return BookAuthor.get_author_books(self.id)

# --------------------------------------------------------------------
# Book Class ---------------------------------------------------------

@dataclass
class Book(Medium):
    """
    A book object consists of:
    :title:       the title of the book
    :publisher:   the publisher of the book
    :publishyear: the year the book was published
    :edition:     edition of the book
    :numpages:    number of pages to read in the book
    :curpage:     current page
    :timesread:   the number of times the book was read
    :rating:      personal rating of the book
    :formattype:  format of the book
    """
    title: str = field(metadata={
        'name': 'Title',
        'desc': 'The title of the book.'})
    publisher: str = field(metadata={
        'name': 'Publisher',
        'desc': 'The book\' publisher.'})
    publishyear: str = field(metadata={
        'name': 'Publish Year',
        'desc': 'The year the book was published.'})
    publishloc: str = field(metadata={
        'name': 'Publish Location',
        'desc': 'The year the book was published.'})
    edition: str = field(metadata={
        'name': 'Edition',
        'desc': 'The edition of the book.'})
    numpages: int = field(metadata={
        'name': 'Number of Pages',
        'desc': 'The number of pages in the book.'})
    formattype: str = field(metadata={
        'name': 'Format',
        'desc': 'The book format (print, ebook, audiobook, etc).'})
    curpage: int = field(default=0, metadata={
        'name': 'Current Page',
        'desc': 'The current page of the book.'})
    timesread: int = field(default=0, metadata={
        'name': 'Times Read',
        'desc': 'The number of times the book was read.'})
    rating: float = field(default=0.0, metadata={
        'name': 'Rating',
        'desc': 'Rating of the book.'})
    
    def __str__(self):
        """Formatted as <title> by <author>, <location>, <year>"""
        return (
            f"{self.title} by {oxford_comma_list(self.author)}, {self.publishloc}, {self.publishyear}"
            )

    @property
    def unique_ids(self) -> list[tuple]:
        """Unique ID definition for a SQL database table."""
        return [('title', self.title),
                ('edition', self.edition)]

    @property
    def author_ids(self) -> list[int]:
        """Get list of the book's author IDs."""
        return BookAuthor.get_book_author_ids(self.id, self.db)

    @property
    def author(self) -> list[str]:
        """Get a list of the book's authors."""
        return BookAuthor.get_book_authors(self.id, self.db)
    
    def store_entry(self, entry:dict) -> None:
        """Store values from a dictionary into the object."""
        for key, val in entry.items():
            setattr( self, self.lut_alias_to_name[key], self.lut_name_to_type[key](val) )

    @classmethod
    def edit_form(self, parent):
        pass

    @property
    def mla_format(self) -> str:
        """MLA citation"""
        pass

    @property
    def apa_format(self) -> str:
        """APA citation"""
        pass

    @property
    def chicago_format(self) -> str:
        """Chicago citation"""
        pass

# --------------------------------------------------------------------
# Books <-> Authors Class --------------------------------------------

@dataclass
class BookAuthor(MediumCreator):
    """Many to many intermediate table to map books and authors."""
    a_name = "author"
    b_name = "book"
    table_name = "books_authors"
    
    @classmethod
    def get_book_author_ids(cls, book_id:int, db) -> list[int]:
        return cls.get_creator_ids(book_id, db)
    
    @classmethod
    def get_book_authors(cls, book_id:int, db) -> list[str]:
        return [Author.load(db, i).first_last for i in cls.get_book_author_ids(book_id, db)]
    
    @classmethod
    def get_author_book_ids(cls, author_id:int, db) -> list[int]:
        return cls.get_media_ids(author_id, db)
    
    @classmethod
    def get_author_books(cls, author_id:int, db) -> list[str]:
        return [Book.load(db, i).title for i in cls.get_author_book_ids(author_id, db)]
    