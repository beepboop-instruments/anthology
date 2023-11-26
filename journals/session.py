"""


"""

# Parent class
from ..database.datatable import *

@dataclass
class Quote(DataTable):
    """
    A quote is direct excerpt copied from a text. It consists of:
    :excerpt:     the actualexcert of text
    :pagenum:     the beginning page number of the excerpt
    :response:    personal response/opinion/reflection on the excerpt
    :sourcetype:  the media format of the source (book, magazine, etc.)
    :source_id:   the datable id number of the source
    :category:    subjects the quote applies to
    """
    excerpt: str
    pagenum: int
    response: str
    sourcetype: str
    source_id: int
    category: list[Category] = field(default_factory=Category)

@dataclass
class Note(DataTable):
    pass

@dataclass
class Session(DataTable):
    """
    A session defines a single occasion of obtaining  information.
    
    A session at minimum consists of:
    :starttime:   session start date and time
    :endtime:     session end date and time
    """
    starttime: str
    endtime: str

@dataclass
class Reading(Session):
    """
    A reading session defines a single occasion of reading some number
    of pages in a book. The process of reading a book is made up of a
    series of reading sessions.
    
    A reading session object consists of:
    :startpage:   first book page read during session
    :endpage:     last book page read during
    :sourcetype:  the media format of the source (book, magazine, etc.)
    :source_id:   the datable id number of the source
    :quotes:      direct quotes highlighted during session
    """
    startpage: int
    endpage: int
    sourcetype: str
    source_id: int
    quotes: list[Quote] = field(default_factory=Quote)

@dataclass
class Lecture(Session):
    """
    """
    pass

@dataclass
class Watching(Session):
    """
    """
    pass

