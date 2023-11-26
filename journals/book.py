"""
Book

"""

# Library imports
from dataclasses import dataclass

# Parent classes
from .medium   import *
from .utils    import oxford_comma_list

# --------------------------------------------------------------------
# Author Class -------------------------------------------------------

@dataclass
class Author(Creator):
    """
    The author class.
    """
    
    @property
    def book_ids(self) -> list[int]:
        """
        Get list of the author's book IDs.
        """
        return BookAuthor.get_author_book_ids(self.id)

    @property
    def books(self) -> list[str]:
        """
        Get a list of the author's books.
        """
        return BookAuthor.get_author_books(self.id)
        
    def mycallback():
        print("Okie dokie.")

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
    """
    title: str
    publisher: str
    publishyear: str
    publishloc: str
    edition: str
    numpages: int
    curpage: int = 0
    timesread: int = 0
    rating: int = 0
    
    def __str__(self):
        """
        Formatted as <title> by <author>, <location>, <year>
        """
        return (
            f"{self.title} by {oxford_comma_list(self.author)}, {self.publishloc}, {self.publishyear}"
            )

    @property
    def unique_ids(self) -> list[tuple]:
        """
        Unique ID definition for a SQL database table.
        """
        return [('title', self.title),
                ('edition', self.edition)]
    
    @property
    def lut(self) -> dict:
        """
        Format attributes into dictionary as:
          { <attribute name> : (<name alias>, <attribute>, <attribute type>) }
        """
        return {
            'title' :       ('Title',            str    ),
            'publisher' :   ('Publisher',        Author ),
            'publishyear' : ('Publish Year',     str    ),
            'publishloc' :  ('Publish Location', str    ),
            'edition' :     ('Edition',          str    ),
            'numpages' :    ('Number of Pages',  int    ),
            'curpage':      ('Current Page',     int    ),
            'timesread' :   ('Times Read',       int    ),
            'rating' :      ('Rating',           int    )
            }

    @property
    def author_ids(self) -> list[int]:
        """
        Get list of the book's author IDs.
        """
        return BookAuthor.get_book_author_ids(self.id, self.db)

    @property
    def author(self) -> list[str]:
        """
        Get a list of the book's authors.
        """
        return BookAuthor.get_book_authors(self.id, self.db)

    @property
    def readable_dict(self) -> dict:
        """
        Format a dictionary by alias and attribute.
        """
        keys = [i[0] for i in self.lut.values()]
        vals = [i[1] for i in self.lut.values()]
        return { k: v for k, v in zip(keys, vals) }
    
    def store_entry(self, entry:dict) -> None:
        """
        Store values from a dictionary into the object.
        """
        for key, val in entry.items():
            setattr( self, self.lut_alias_to_name[key], self.lut_name_to_type[key](val) )

    @classmethod
    def edit_form(self, parent):
        pass

    @property
    def mla_format(self) -> str:
        """
        MLA citation
        """
        pass

    @property
    def apa_format(self) -> str:
        """
        APA citation
        """
        pass

    @property
    def chicago_format(self) -> str:
        """
        Chicago citation
        """
        pass

# --------------------------------------------------------------------
# Books <-> Authors Class --------------------------------------------

@dataclass
class BookAuthor(MediumCreator):
    """
    Many to many intermediate table to map books and authors.
    """
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
    