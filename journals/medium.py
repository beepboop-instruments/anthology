"""
Media

"""

# Library package imports
from abc import abstractclassmethod

# Parent class
from ..database.datatable import *

# --------------------------------------------------------------------
# Medium Class -------------------------------------------------------

@dataclass
class Medium(DataTable, ABC):
    """ Class to define media stored in the database. """
    
    @classmethod
    def nice(self):
        pass

    @abstractmethod
    def readable_dict(self):
        pass

    @abstractmethod
    def store_entry(self):
        pass

# --------------------------------------------------------------------
# Creator Class ------------------------------------------------------

@dataclass
class Creator(DataTable, ABC):
    """
    A creator consists of:
    :firstname:  creator's first name
    :midname:    creator's middle name
    :lastname:   creator's last name
    :gender:     creator's gender
    :country:    creator's country of association
    """
    firstname: str = ""
    lastname: str = ""
    midname: str = ""
    gender: str = ""
    country: str = ""
    
    def __str__(self):
        return self.last_first
    
    @classmethod
    def lut(cls) -> dict:
        """
        Format attributes into dictionary as:
          { <attribute name> : (<name alias>, <attribute>, <attribute type>) }
        """
        return {
            'firstname' : ('First Name',  str ),
            'midname' :   ('Middle Name', str ),
            'lastname' :  ('Last Name',   str ),
            'gender' :    ('Gender',      str ),
            'country' :   ('Country',     str )
            }

    @property
    def unique_ids(self) -> list[tuple]:
        return [('firstname', self.firstname),
                ('midname', self.midname),
                ('lastname', self.lastname)]

    @property
    def first_last(self):
        return f"{self.firstname} {self.midname} {self.lastname}"

    @property
    def last_first(self):
        return f"{self.lastname}, {self.firstname} {self.midname}"
 
# --------------------------------------------------------------------
# Medium <--> Creator Class ------------------------------------------

@dataclass
class MediumCreator(RelTable, ABC):
    """
    Many to many intermediate table to map media and creators.
    
    A table: Creators
    B table: Media
    """
 
    @classmethod
    def get_creator_ids(cls, medium_id:int, db) -> list[int]:
        return cls.lookup_rel_ids(db, medium_id, ("b","a"))
    
    @classmethod
    def get_media_ids(cls, creator_id:int, db) -> list[int]:
        return cls.lookup_rel_ids(db, creator_id, ("a","b"))
     
# --------------------------------------------------------------------
# Category Class -----------------------------------------------------

@dataclass
class Category(DataTable, ABC):
    """ A parent class for categorizing media items. """
    name: str

# --------------------------------------------------------------------
# Genre Class --------------------------------------------------------

@dataclass
class Genre(Category):
    """ A genre within the medium (fiction, non-fiction, etc.). """

# --------------------------------------------------------------------
# Sub-Genre Class ----------------------------------------------------

@dataclass
class SubGenre(Category):
    """ A sub-genre within a medium (science-fiction, horror, etc.) """

# --------------------------------------------------------------------
# Subject Class ------------------------------------------------------

@dataclass
class Subject(Category):
    """
    A subject within the medium (engineering, philosophy, etc.)
    :synonyms:   list of similar key words that might help searching
    """
    synonyms: list[str] = field(default_factory=list)
