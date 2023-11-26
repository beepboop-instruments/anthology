from datetime import date
from icecream import ic
import unittest, pytest, yaml, json

# Library imports
from datetime import datetime, timedelta

# UUT import
from anthology.journals.book import Book, Author, BookAuthor
from anthology.database.config import DBCfg
        
test_db = DBCfg("./db/test.db")

# --------------------------------------------------------------------
# Helper functions ---------------------------------------------------

def save_load_check(self, cls, obj) -> None:
    """
    Save an object to a database. Load it and check that it was 
    loaded as saved.
    """
    
    # add to database
    obj.create()
    new_id = obj.save()

    # read it from database
    if new_id:
        read_obj = cls.load(obj.db, new_id)
    else:
        return

    # check eqality
    self.assertEqual(obj, read_obj)


# --------------------------------------------------------------------
# Test sequence ------------------------------------------------------

class TestBook(unittest.TestCase):

    def test_book(self):
        """
        Define a new Book, store it in the databae, load it from the
        database, and check equality.
        """

        BookAuthor.create(test_db)

        # define a new Author object
        uut_author = [
            Author(
            db = test_db,
            firstname = "Terry",
            lastname = "Cotta",
            midname = "J",
            gender = "Female",
            country = "Here In the World"
            ),
            Author(
            db = test_db,
            firstname = "Barry",
            lastname = "Winstor",
            midname = "P",
            gender = "Female",
            country = "Here In the World"
            ),
            Author(
            db = test_db,
            firstname = "Tonsil",
            lastname = "McItus",
            midname = "Cookie",
            gender = "Female",
            country = "Here In the World"
            )
            ]
        # save and load it from database
        for a in uut_author:
            save_load_check(self, Author, a)
        
        # define new Book object
        uut_book = Book(
            db = test_db,
            title = "A Book to Test the Book Class",
            publisher = "Big Books",
            publishyear = 2021,
            publishloc = "Ellicott City, MD",
            edition = "First",
            numpages = 500
            )
        # save and load it from database
        save_load_check(self, Book, uut_book)
        
        # assign authors to a book
        if uut_book.id:
            for a in uut_author:
                BookAuthor(test_db).save((a.id, uut_book.id))
        
        ic(Book.load_table(test_db))
        ic(Author.load_table(test_db))
        ic(BookAuthor.load_table(test_db))
        
        ic(uut_book.__match_args__)


if __name__ == '__main__':
    unittest.main()
