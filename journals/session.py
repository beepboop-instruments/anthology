"""
Session

"""

# Package imports
from datetime import datetime, timedelta

# Parent class
from ..database.datatable import *
from .medium import Category

@dataclass
class Quote(DataTable):
    """
    A quote is direct excerpt copied from a text. It consists of:
    :excerpt:     the actual excerpt of text
    :pagenum:     the beginning page number of the excerpt
    :response:    personal response/opinion/reflection on the excerpt
    :sourcetype:  the media format of the source (book, magazine, etc.)
    :source_id:   the datable id number of the source
    :category:    subjects the quote applies to
    """
    excerpt: str = field(metadata={
        'name': 'Excerpt',
        'desc': 'The quoted text excerpt.'})
    pagenum: int = field(metadata={
        'name': 'Page Number',
        'desc': 'The beginning page number of the excerpt.'})
    response: str = field(metadata={
        'name': 'Response',
        'desc': 'A personal response, opinion, or reflection on the excerpt.'})
    sourcetype: str = field(metadata={
        'name': 'Media Format',
        'desc': 'The media format of the quoted source.'})
    
    @property
    def unique_ids(self) -> list[tuple]:
        return [('excerpt', self.excerpt)]

@dataclass
class Note(DataTable):
    pass

@dataclass
class Session(DataTable):
    """
    A session defines a single occasion of obtaining information.
    
    A session at minimum consists of:
    :start_time:   session start date and time
    :end_time:     session end date and time
    """
    start_time: datetime = field(metadata={
        'name': 'Start Time',
        'desc': 'The session start date and time.'})
    end_time: datetime = field(metadata={
        'name': 'End Time',
        'desc': 'The session end date and time.'})
    
    @property
    def duration(self) -> str:
        """
        Return the difference between the start and end times in minutes.
        """
        # Find delta in seconds
        delta = int((self.end_time - self.start_time).total_seconds())
        # Determine hours and minutes from seconds
        hrs = delta // 3600
        mins = (delta % 3600) // 60
        # Format number of hours and mins into strings
        if hrs:
            hr_str = f"{str(hrs)} hr{'s'[:hrs^1]} & "
        else:
            hr_str = ""
        min_str = f"{str(mins)} min{'s'[:mins^1]}"
        
        return f"{hr_str}{min_str}"

@dataclass
class Reading(Session):
    """
    A reading session defines a single occasion of reading some number
    of pages in a book. The process of reading a book is made up of a
    series of reading sessions.
    
    A reading session object consists of:
    :start_page:   first book page read during session
    :end_page:     last book page read during
    :source_type:  the media format of the source (book, magazine, etc.)
    :source_id:    the datable id number of the source
    :quotes:       direct quotes highlighted during session
    """
    start_page: int = field(metadata={
        'name': 'Start Page',
        'desc': 'The first page read during the session.'})
    end_page: int = field(metadata={
        'name': 'End Page',
        'desc': 'The last page read druing the session.'})
    source_type: str = field(metadata ={
        'name': 'Format',
        'desc': 'The media format.'})
    _source_id: int
    _quotes: list[Quote] = field(default_factory=Quote)
    
    @classmethod
    def lut(cls) -> dict:
        return {}
    
    @property
    def unique_ids(self) -> list[tuple]:
        return [('start_time', self.start_time),
                ('end_time', self.end_time)]
    
    @property
    def num_pages_read(self) -> int:
        """Return the number of pages read from the start page to end page."""
        return self.end_page - self.start_page

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

# --------------------------------------------------------------------
# Readings <-> Quotes Class ------------------------------------------

@dataclass
class ReadingQuote(RelTable):
    """Many to many intermediate table to map readings and quotes."""
    a_name = "reading"
    b_name = "quote"
    table_name = "readings_quotes"
    
    @classmethod
    def get_reading_quote_ids(cls, reading_id:int, db) -> list[int]:
        """Return a list of quote ids associated with a reading id."""
        return cls.lookup_rel_ids(db, reading_id, ("b","a"))
    
    @classmethod
    def get_reading_quotes(cls, reading_id:int, db) -> list[str]:
        """Return a list of quotes associated with a reading id."""
        return [Quote.load(db, i) for i in cls.get_reading_quote_ids(reading_id, db)]
    
    @classmethod
    def get_quote_reading_ids(cls, quote_id:int, db) -> list[int]:
        """Return a list of reading ids associated with a quote id."""
        return cls.lookup_rel_ids(db, quote_id, ("a","b"))
    
    @classmethod
    def get_quote_readings(cls, quote_id:int, db) -> list[str]:
        """Return a list of readings associated with a quote id."""
        return [Reading.load(db, i).title for i in cls.get_quote_reading_ids(quote_id, db)]