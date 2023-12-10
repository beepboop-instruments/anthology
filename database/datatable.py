"""
Data Table Module

"""

# Library imports
from typing      import List, Any, Iterable
from dataclasses import dataclass, field, fields
from abc         import ABC, abstractmethod
from loguru      import logger
import datetime

# Module imports
from .config     import DBCfg

# Constants
SQL_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
ERROR_UNSUPPORTED_TYPE = "Unsupported data type for SQL translation! {KEY_TYPE} : {KEY_VAR}"

# ---------------------------------------------------------------------
# Helper functions ----------------------------------------------------

def is_date(
    string : str,
    date_format : str | Iterable[str]=('%Y-%m-%d %H:%M:%S')
    ) -> bool:
    """Check if a string is formatted as a valid date.

    Parameters
    ----------
    string : str
        The string to check for dateness.
    date_format : hashable, optional(default=('%Y-%m-%d %H:%M:%S'))
        A iterable of strings containing the date formats to check for.
    
    Returns
    -------
    bool: True if the string is in a valid date format.
    """
 
    for format in date_format:
        try: 
            datetime.datetime.strptime(string, format)
            return True
        except ValueError:
            pass
        
    # If this is reached, the string could not be converted to a date
    return False

def params_to_str(params : dict) -> str:
    """Convert a parameters dictionary to a SQL row string.

    Parameters
    ----------
    params : dict
        A dictionary of parameters to convert to a string.
    
    Returns
    -------
    str: A string formated into a SQL data row.
    """
    
    # Add each item to the returned string based on its type.
    param_str = ""
    for key, val in params.items():
        param_str += f"{key} = "
        if isinstance(val, (int, bool, float)):
            param_str += f"{val}, "
        elif isinstance(key, (datetime.datetime)):
            param_str += f"\'{str(val)}\',"
        else:
            param_str += f"\'{val}\', "
    
    return param_str[:-2]

def get_sql_type(var : Any) -> str:
    """Get the SQL data type keyword for a given variable.
    
    Parameters
    ----------
    var : any
        The variable to get the SQL data type keyword of.
    
    Returns
    -------
    str: A string of the SQL data type keyword.
    
    Raises
    ------
    ValueError if the variable is an unsupported type.
    """
    
    if isinstance(var, (int, bool)):
        return "INTEGER"
    elif isinstance(var, float):
        return "REAL"
    elif isinstance(var, (complex, str, list, dict, tuple,
                            range, set, frozenset, bytes,
                            bytearray, memoryview) ):
        return "TEXT"
    elif isinstance(var, (datetime.datetime)):
        return "DATETIME"
    else:
        error_msg = ERROR_UNSUPPORTED_TYPE.format(KEY_TYPE=type(var), KEY_VAR=var)
        logger.error(error_msg)
        raise ValueError(error_msg)

def get_sql_value(var : Any) -> Any:
    """Get the SQL data value for a given variable.
    
    Format values submitted to a SQL database in the applicable format.
    For example, booleans should be 1 or 0. Dates and lists are formatted
    as strings.
    
    Parameters
    ----------
    var : any
        The variable to get the formatted SQL value of.
        
    Returns
    ------
    any : The formatted SQL variable
    
    Input parameters:
    :var:  Python variable whose SQL formatted value to return.
    """
    if isinstance(var, (int, bool)):
        return int(var)
    elif isinstance(var, float):
        return var
    elif isinstance(var, (complex, str, Iterable, datetime.datetime)):
        return str(var)
    else:
        error_msg = ERROR_UNSUPPORTED_TYPE.format(KEY_TYPE=type(var), KEY_VAR=var)
        logger.error(error_msg)
        raise ValueError(error_msg)

# ---------------------------------------------------------------------
# DataTable Class -----------------------------------------------------

@dataclass
class DataTable(ABC):
    """SQL data table class.
    
    A generic object consisting of the minimal table parameters and
    methods to interact with a SQL database. This is a parent class to
    the more specific types of data tables.
    
    Attributes
    ----------
    db : DBCfg (Database Config Object)
        Contains the SQL database interface.
    id : int
        An item in the DataTable's unique ID.
    
    Methods
    -------
    create
        Add the table to the database if it does not already exist.
    list_all
        List everything in the data table by its __str__ value.
    load
        Load an item from the data table.
    load_column
        Load all values in a data table column
    load_table
        Load everything from the data table.
    lut_aliases
        Get a list of formal print names for each parameter.
    lut_alias_to_desc
        Get a list of formal print names to descriptions of each parameter.
    lut_alias_to_var
        Get a dictionary of formal print names to each parameter.
    lut_var_to_alias
        Get a dictionary of parameter names to format print names.
    lut_var_to_desc
        Get a dictionary of parameter names to descrtiptions of each parameter.
    lut_var_to_type(cls)
        Get a dictionary of parameter names to object type.
    save
        Save an item to the data table.
    """
    
    db: DBCfg = field()
    id: int = field(init=False, default_factory=int)

    def create(self) -> None:
        """Add table to the database if it does not exist.
        
        Iterate through each parameter to define the table's columns.
        Then, save the table to the database in db.
        
        Returns
        -------
        None
        """

        # Format all of the object's parameters into a string.
        cols = ""
        for i in self.__dict__:
            if i == 'id':
                cols += "id INTEGER PRIMARY KEY, "
            elif i == 'db':
                pass
            else:
                cols += f"{i} {get_sql_type(self.__dict__[i])}, "
        if self.unique_ids[0][0]:
            cols += f"{self.unique_str}, "

        sql = f"""CREATE TABLE IF NOT EXISTS {self.__class__.__name__}s({cols[:-2]});"""

        logger.debug(f"Creating {self.__class__.__name__}s table (if it doesn't exist).")
        # Store in the SQL database.
        self.db.cursor.execute(sql)

    @classmethod
    def load(cls, db : DBCfg, val : Any, col : str="id"):
        """ Load a row from an SQL table.
       
        Query for a specific value in a specified column.
        
        Parameters
        ----------
        db : DBCfg (Database Configuration object)
            Contains the SQL database interface.
        val : any
            The value to lookup within the column.
        col : str
            The column name to search within.
        
        Returns
        -------
        An initialized object loaded from the database.
        """

        # Format the SQL query to a string.
        sql = f"SELECT * FROM {cls.__name__}s WHERE {col}=?"

        # Query the database
        db.cursor.execute(sql, (val,))
        row = db.cursor.fetchone()
        if not row:
            logger.debug(f"Did not find {col}: {val} in {cls.__name__}s")
            return 0
        else:
            logger.debug(f"Read {col}: {val} - {row}")

        # Parse the row values into the object's fields.
        params = []
        for i in row:
            if isinstance(i, str) and i[0] == '[':
                params.append(eval(i))
            elif isinstance(i, str) and is_date(i):
                params.append(datetime.datetime.strptime(i, SQL_DATE_FORMAT))
            else:
                params.append(i)
        obj = cls(*params[:])
        obj.id = params[0]
        obj.db = db
        logger.debug(f"Successfully loaded {cls.__name__}: {obj}")

        return obj

    @classmethod
    def load_table(cls, db : DBCfg) -> list[Any]:
        """Read an entire table from the database.
        
        Parameters
        ----------
        db : DBCfg (Database Configuration object)
            Contains the SQL database interface.
        
        Returns
        -------
        A list of all loaded items from the database.
        """
        
        logger.debug(f"Reading entire {cls.__name__} table.")
        db.cursor.execute(f"SELECT * FROM {cls.__name__}s")
        return db.cursor.fetchall()
    
    @classmethod
    def load_column(cls, db : DBCfg, col : str) -> list[Any]:
        """Read all distinct values in a column.
        
        Parameters
        ----------
        db : DBCfg (Database Configuration object)
            Contains the SQL database interface.
        col : str
            The column to load all values from.
        
        Returns
        -------
        A list of all values read from the column in the data table.
        
        """
        logger.debug(f"Reading {col} from {cls.__name__} table.")
        db.cursor.execute(f"SELECT DISTINCT {col} FROM {cls.__name__}s")
        return [i[0] for i in db.cursor.fetchall()]
    
    @classmethod
    def list_all(cls, db) -> list[str]:
        """List all items in a table by its __str__ value.
        
        Parameters
        ----------
        db : DBCfg (Database Configuration object)
            Contains the SQL database interface.
        
        Returns
        -------
        A list of all items in a table in their __str__ format.
        """
        
        logger.debug(f"Listing all items in {cls.__name__} table.")
        return [str(cls.load(db, i)) for i in cls.load_column(db, "id")]
 
    def save(self, update=True) -> int:
        """Write an object's values to a SQL data table.
        
        Parameters
        ----------
        update : bool
            If true, updates all values of the item in the data table as
            opposed to adding a new instance to the data table.
        
        Returns
        -------
        int : the ID of the object just saved to the database.
        """
        
        # Format all of the object's parameters into a string.
        params = list(self.__dict__.keys())
        params.remove('db')
        params.remove('id')
        cols = ", ".join([str(s) for s in params])
        q = ("?,"*len(params))[:-1]
        
        if self.id == 0:
            # Add new row to the table.
            vals = tuple([get_sql_value(self.__dict__[i]) for i in params])
            logger.debug(f"Writing {self.__class__.__name__} table: {vals}")
            
            sql = f"""
                    INSERT INTO {self.__class__.__name__}s({cols})
                    VALUES({q})
                   """
            try:
                self.db.cursor.execute(sql, vals)
            except Exception as e:
                logger.error(f"Failed to save: {self.__class__.__name__}: {vals}")
                logger.error(e)
                return 0
        elif update:
            # Update a row in the table.
            sql = f"""
                     UPDATE {self.__class__.__name__}s
                     SET {params_to_str(self.__dict__)}
                     WHERE id = {self.id}
                   """
            self.db.cursor.execute(sql)
        else:
            logger.warning(f"Did not save {self.__class__.__name__}: {self}")
            return 0
        
        # store to database
        self.db.conn.commit()

        # Read and set the instance's ID.
        self.id = self.db.cursor.execute(
            f"SELECT last_insert_rowid() FROM {self.__class__.__name__}s"
            ).fetchone()[0]
        
        return self.id
    
    @abstractmethod
    def unique_ids(self) -> list[tuple]:
        """Unique constraints to avoid storing duplicate items to the database."""
        pass
    
    @property
    def unique_str(self) -> str:
        """A string of the unique IDs formatted for a SQL command."""
        return f"UNIQUE ({', '.join([i[0] for i in self.unique_ids])})"
    
    @classmethod
    def lut_aliases(cls) -> list:
        """Return a list of formal print names."""
        return [f.metadata['name'] for f in fields(cls) if f.metadata]

    @classmethod
    def lut_alias_to_var(cls) -> dict:
        """Return a dictionary of formal print names to field names."""
        return { f.metadata['name'] : f.name for f in fields(cls) if f.metadata }
    
    @classmethod
    def lut_alias_to_desc(cls) -> dict:
        """Return a dictionary of formal print names to field descriptions."""
        return { f.metadata['name'] : f.metadata['desc'] for f in fields(cls) if f.metadata }
    
    @classmethod
    def lut_var_to_alias(cls) -> dict:
        """Return a dictionary of field names to formal print names."""
        return { f.name : f.metadata['name'] for f in fields(cls) if f.metadata }
    
    @classmethod
    def lut_var_to_type(cls) -> dict:
        """Return a dictionary of field names to field types."""
        return { f.name : f.type.__name__ for f in fields(cls) if f.metadata }
    
    @classmethod
    def lut_var_to_desc(cls) -> dict:
        """Return a dictionary of field names to field descriptions."""
        return { f.name : f.metadata['desc'] for f in fields(cls) if f.metadata }

# ---------------------------------------------------------------------
# RelTable Class ------------------------------------------------------

@dataclass
class RelTable(ABC):
    """A relational table to map two tables in a SQL database.
    
    Attributes
    ----------
    db : DBCfg (Database Config Object)
        Contains the SQL database interface.
    
    Methods
    -------
    create
        Creates the table in the database if it does not exist.
    lookup_rel_ids
        
    """
    db: DBCfg

    @classmethod
    def create(cls, db : DBCfg):
        """Create a many to many relational table if it does not exist.
        
        Parameters
        ----------
        db : DBCfg (Database Config Object)
            Contains the SQL database interface.
        
        Returns
        -------
        None
        
        """
        
        sql = f""" CREATE TABLE IF NOT EXISTS {cls.table_name} (
                     {cls.a_name}_id integer NOT NULL,
                     {cls.b_name}_id integer NOT NULL,
                     FOREIGN KEY ({cls.a_name}_id) REFERENCES {cls.a_name}s(id), 
                     FOREIGN KEY ({cls.b_name}_id) REFERENCES {cls.b_name}s(id),
                     UNIQUE ({cls.a_name}_id, {cls.b_name}_id)
                     ); """
        logger.debug(f"Creating {cls.table_name} with {cls.a_name}_id and {cls.b_name}_id")
        
        # Store in the SQL database.
        db.cursor.execute(sql)

    @classmethod
    def lookup_rel_ids(cls, db : DBCfg, id : int, x_in_y : tuple=("a", "b")) -> list:
        """List all IDs in a column mapped to the specified ID in the other column.
        
        Parameters
        ----------
        db : DBCfg (Database Config Object)
            Contains the SQL database interface.
        id : int
            The ID to lookup all mappings to.
        x_in_y : tuple, optional(default=('a', 'b'))
            Defines which table to find the IDs in the other.
            For example, ('a', 'b') looks for all items in b that
            map to the id of the value found in 'a'.b that map to
            
        Returns
        -------
        list : a list of the IDs that map to the input id.
        """
        # Set which table to search first
        if x_in_y[0] == "a":
            x_name = cls.a_name
            y_name = cls.b_name
            col=1
        else:
            x_name = cls.b_name
            y_name = cls.a_name
            col=0

        # Format the SQL query to a string.
        sql = f"SELECT * FROM {cls.table_name} WHERE {x_name}_id=?"

        # Query the database
        db.cursor.execute(sql, (id,))
        rows = db.cursor.fetchall()

        # Format the y table's id's into a list
        ids = [i[col] for i in rows]
        logger.debug(f"Found {y_name} IDs in {x_name} table: {ids}")

        return ids

    @classmethod
    def load_table(cls, db : DBCfg) -> list[Any]:
        """Load an entire table from a database.
        
        Parameters
        ----------
        db : DBCfg (Database Config Object)
            Contains the SQL database interface.
            
        Returns
        -------
        list : a list of all items in the data table.
        
        """
        logger.debug(f"Reading entire {cls.__name__} table.")
        db.cursor.execute(f"SELECT * FROM {cls.table_name}")
        return db.cursor.fetchall()
    
    def save(self, row : tuple) -> int:
        """Add a row to the table.
        
        Parameters
        ----------
        row : tuple
            Define the row of mapped IDs to save.
            
        Returns
        -------
        int : the ID of the saved row.
        
        """
        a_id, b_id = row
        
        logger.debug(f"Writing {row} into {self.table_name}")
        
        sql = f""" INSERT INTO {self.table_name}({self.a_name}_id, {self.b_name}_id)
              VALUES(?,?)"""
        try:
            self.db.cursor.execute(sql, (a_id, b_id))
            self.db.conn.commit()
        except Exception as e:
            logger.error(f"Failed to save: {self.table_name}: {row}")
            logger.error(e)
            return 0
        
        # Read and set the instance's ID.
        self.id = self.db.cursor.execute(
            f"SELECT last_insert_rowid() FROM {self.table_name}"
            ).fetchone()[0]
        logger.debug(f"Saved {self.table_name} ID: {self.id}")
        
        return self.id