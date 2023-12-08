
# Package imports
import unittest, yaml

# Module imports
from anthology.journals.session import Reading
from anthology.database.config import DBCfg

# Test data file containing UUT test parameters and expected results
FILE_UUT_SESSION = "./anthology/test/uut_session.yaml"

class TestSession(unittest.TestCase):
    """Test the session module."""
    
    def __init__(self, *args, **kwargs):
        super(TestSession, self).__init__(*args, **kwargs)
        with open(FILE_UUT_SESSION, 'r') as f:
            self.uut = yaml.safe_load(f)
            self.test_db = DBCfg(self.uut["database"])
            # Define a Reading object
            self.reading = Reading(db=self.test_db, **self.uut["reading_session"]["uut"])
    
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


if __name__ == '__main__':
    unittest.main()