
# Package imports
import unittest, yaml

# Module imports
from anthology.journals.session import Reading, Quote, ReadingQuote
from anthology.database.config import DBCfg

# Test data file containing UUT test parameters and expected results
FILE_UUT_SESSION = "./anthology/test/uut_session.yaml"

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

class TestSession(unittest.TestCase):
    """Test the session module."""
    
    def __init__(self, *args, **kwargs):
        super(TestSession, self).__init__(*args, **kwargs)
        with open(FILE_UUT_SESSION, 'r') as f:
            self.uut = yaml.unsafe_load(f)
            self.test_db = DBCfg(self.uut["database"])
            # Define a Reading object
            self.reading = Reading(db=self.test_db, **self.uut["reading_session"]["uut"])
            # Initialize the Quote list UUT
            self.quotes = [Quote(db=self.test_db, **params) for params in self.uut["quotes"]["uut"].values()]
    
    def test_metadata(self):
        """Test the expected metadata and look-up-table functions."""
        self.assertEqual(
            Reading.lut_var_to_alias(),
            self.uut["reading_session"]["results"]["lut_var_to_alias"],
            msg=f"Unexpected look-up-table field name to alias!"
        )
        self.assertEqual(
            Reading.lut_var_to_type(),
            self.uut["reading_session"]["results"]["lut_var_to_type"],
            msg=f"Unexpected look-up-table field name to type!"
        )
        self.assertEqual(
            Reading.lut_var_to_desc(),
            self.uut["reading_session"]["results"]["lut_var_to_desc"],
            msg=f"Unexpected look-up-table field name to description!")
        self.assertEqual(
            Reading.lut_alias_to_var(),
            self.uut["reading_session"]["results"]["lut_alias_to_var"],
            msg=f"Unexpected look-up-table alias to field name!"
        )
        self.assertEqual(
            Reading.lut_alias_to_desc(),
            self.uut["reading_session"]["results"]["lut_alias_to_desc"],
            msg=f"Unexpected look-up-table alias to description!"
        )
        
    def test_duration(self):
        """Test the duration function"""
        self.assertEqual(
            self.reading.duration,
            self.uut["reading_session"]["results"]["duration"],
            msg=f"Unexpected reading session duration!"
        )
        
    def test_num_pages_read(self):
        """Test the number of pages read function"""
        self.assertEqual(
            self.reading.num_pages_read,
            self.uut["reading_session"]["results"]["num_pages_read"],
            msg=f"Unexpected number of pages read!")

    def test_reading_save(self):
        """
        Define a new Reading, store it in the database, load it from the
        database, and check equality.
        """

        ReadingQuote.create(self.test_db)

        # save and load it from database
        for q in self.quotes:
            save_load_check(self, Quote, q)
        
        # save and load it from database
        save_load_check(self, Reading, self.reading)
        
        # assign quotes to a reading
        if self.reading.id:
            for q in self.quotes:
                ReadingQuote(self.test_db).save((q.id, self.reading.id))

        # test the database load table functions
        self.assertEqual(
            Reading.load_table(self.test_db),
            self.uut["reading_session"]["results"]["reading_load_table"],
            msg=f"Unexpected data loaded from database!")
        self.assertEqual(
            Quote.load_table(self.test_db),
            self.uut["quotes"]["results"],
            msg=f"Unexpected data loaded from database!")
        self.assertEqual(
            ReadingQuote.load_table(self.test_db),
            self.uut["reading_session"]["results"]["reading_quote"],
            msg=f"Unexpected data loaded from database!")


if __name__ == '__main__':
    unittest.main()