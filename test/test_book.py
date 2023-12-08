from icecream import ic
import unittest, pytest, yaml, os

# Library imports
from dataclasses import fields

# UUT import
from anthology.journals.book import Book, Author, BookAuthor
from anthology.database.config import DBCfg

# Test data file containing UUT test parameters and expected results
FILE_UUT_SESSION = "./anthology/test/uut_book.yaml"

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
    """Test the Book class."""
    
    def __init__(self, *args, **kwargs):
        super(TestBook, self).__init__(*args, **kwargs)
        with open(FILE_UUT_SESSION, 'r') as f:
            self.uut = yaml.unsafe_load(f)
            self.test_db = DBCfg(self.uut["database"])
            # Initialize the Book UUT
            self.book = Book(db=self.test_db, **self.uut["book"]["uut"])
            # Initialize the Author list UUT
            self.authors = [Author(db=self.test_db, **params) for params in self.uut["authors"]["uut"].values()]
    
    def test_metadata_book(self):
        """Test the expected metadata and look-up-table functions."""
        self.assertEqual(
            Book.lut_var_to_alias(),
            self.uut["book"]["results"]["lut_var_to_alias"],
            msg=f"Unexpected look-up-table field name to alias!"
        )
        self.assertEqual(
            Book.lut_var_to_type(),
            self.uut["book"]["results"]["lut_var_to_type"],
            msg=f"Unexpected look-up-table field name to type!"
        )
        self.assertEqual(
            Book.lut_var_to_desc(),
            self.uut["book"]["results"]["lut_var_to_desc"],
            msg=f"Unexpected look-up-table field name to description!")
        self.assertEqual(
            Book.lut_alias_to_var(),
            self.uut["book"]["results"]["lut_alias_to_var"],
            msg=f"Unexpected look-up-table alias to field name!"
        )
        self.assertEqual(
            Book.lut_alias_to_desc(),
            self.uut["book"]["results"]["lut_alias_to_desc"],
            msg=f"Unexpected look-up-table alias to description!"
        )
        
    def test_metadata_authors(self):
        """Test the expected metadata and look-up-table functions."""
        self.assertEqual(
            Author.lut_var_to_alias(),
            self.uut["authors"]["results"]["lut_var_to_alias"],
            msg=f"Unexpected look-up-table field name to alias!"
        )
        self.assertEqual(
            Author.lut_var_to_type(),
            self.uut["authors"]["results"]["lut_var_to_type"],
            msg=f"Unexpected look-up-table field name to type!"
        )
        self.assertEqual(
            Author.lut_var_to_desc(),
            self.uut["authors"]["results"]["lut_var_to_desc"],
            msg=f"Unexpected look-up-table field name to description!")
        self.assertEqual(
            Author.lut_alias_to_var(),
            self.uut["authors"]["results"]["lut_alias_to_var"],
            msg=f"Unexpected look-up-table alias to field name!"
        )
        self.assertEqual(
            Author.lut_alias_to_desc(),
            self.uut["authors"]["results"]["lut_alias_to_desc"],
            msg=f"Unexpected look-up-table alias to description!"
        )

    def test_book_save(self):
        """
        Define a new Book, store it in the databae, load it from the
        database, and check equality.
        """

        BookAuthor.create(self.test_db)

        # save and load it from database
        for a in self.authors:
            save_load_check(self, Author, a)
        
        # save and load it from database
        save_load_check(self, Book, self.book)
        
        # assign authors to a book
        if self.book.id:
            for a in self.authors:
                BookAuthor(self.test_db).save((a.id, self.book.id))

        # test the database load table functions
        self.assertEqual(
            Book.load_table(self.test_db),
            self.uut["book"]["results"]["book_load_table"],
            msg=f"Unexpected data loaded from database!")
        self.assertEqual(
            Author.load_table(self.test_db),
            self.uut["book"]["results"]["authors_load_table"],
            msg=f"Unexpected data loaded from database!")
        self.assertEqual(
            BookAuthor.load_table(self.test_db),
            self.uut["book"]["results"]["book_authors_load_table"],
            msg=f"Unexpected data loaded from database!")


if __name__ == '__main__':
    unittest.main()
