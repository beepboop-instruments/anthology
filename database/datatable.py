"""
Data Table Module

"""

# Library imports
from typing      import List, Any
from dataclasses import dataclass, field, fields
from abc         import ABC, abstractmethod
from loguru      import logger
import datetime

# Module imports
from .config     import DBCfg

SQL_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# --------------------------------------------------------------------
# Helper functions ---------------------------------------------------

def is_date(string):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    """
    try: 
        datetime.datetime.strptime(string, SQL_DATE_FORMAT)
        return True

    except ValueError:
        return False

def params_to_str(params:dict) -> str:
    """
    Convert a dictionary of parameters to a string for updating a
    row in the data table.
    """
    param_str = ""
    for p in params.keys():
        param_str += f"{p} = "
        if isinstance(params[p], (int, bool, float)):
            param_str += f"{params[p]}, "
        elif isinstance(p, (datetime.datetime)):
            param_str += f"\'{str(params[p])}\',"
        else:
            param_str += f"\'{params[p]}\', "
    
    return param_str[:-2]

def get_sql_type(var:Any) -> str:
    """
    Get the SQL data type for a given Python variable.
    
    Input parameters:
    :var:  Python variable whose SQL type to return.
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
        logger.error(f"Unknown data type for SQL translation! {type(var)} : {var}")
        return "NULL"

def get_sql_value(var:Any) -> Any:
    """
    Get the SQL data value for a given Python variable.
    
    Input parameters:
    :var:  Python variable whose SQL formatted value to return.
    """
    if isinstance(var, (int, bool)):
        return int(var)
    elif isinstance(var, float):
        return var
    elif isinstance(var, (complex, str, list, datetime.datetime)):
        return str(var)
    else:
        logger.error(f"Unknown data type for SQL translation! {type(var)} : {var}")
        return "NULL"

# --------------------------------------------------------------------
# DataTable Class ----------------------------------------------------

@dataclass
class DataTable(ABC):
    db: DBCfg = field()
    id: int = field(init=False, default_factory=int)

    def create(self):
        """
        Add table to the database if it does not exist. Iterate
        through each parameter to define the table's columns.
        Then, save it to the database.
        """

        # Format all of the objects parameters into string.
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
    def load(cls, db, val:Any, col:str="id"):
        """
        Load a row from an SQL table by querying for a specific value
        in a specified column.
        
        Input parameters:
        :val: the value to search for within the column.
        :col: the table column to search.
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
    def load_table(cls, db) -> list[Any]:
        """
        Read an entire table from the database.
        """
        logger.debug(f"Reading entire {cls.__name__} table.")
        db.cursor.execute(f"SELECT * FROM {cls.__name__}s")
        return db.cursor.fetchall()
    
    @classmethod
    def load_column(cls, db, col) -> list[Any]:
        """
        Read all distinct values in a column.
        """
        logger.debug(f"Reading {col} from {cls.__name__} table.")
        db.cursor.execute(f"SELECT DISTINCT {col} FROM {cls.__name__}s")
        return [i[0] for i in db.cursor.fetchall()]
    
    @classmethod
    def list_all(cls, db) -> list[str]:
        """
        Provide list of all items in the table.
        """
        logger.debug(f"Listing all items in {cls.__name__} table.")
        return [str(cls.load(db, i)) for i in cls.load_column(db, "id")]
 
    def save(self, update=True):
        """
        Write an instance's values to a SQL data table.
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
        pass
    
    @property
    def unique_str(self) -> str:
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

# --------------------------------------------------------------------
# RelTable Class -----------------------------------------------------

@dataclass
class RelTable(ABC):
    """
    An intermediate relational table for many to many mappings between
    two tables in a SQL database.
    """
    db: DBCfg

    @classmethod
    def create(cls, db):
        """
        Create a many to many relational table if it does not exist.
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
    def lookup_rel_ids(cls, db, id:int, x_in_y:tuple=("a","b")) -> list:
        """
        Load a row from an SQL table by querying for a specific value
        in a specified column.
        
        Input parameters:
        :val:    the value to search for within the column.
        :col:    the table column to search.
        :x_in_y: which table to search for a value from the other
                 e.g., (a,b) looks for all items in b that map to
                 the id of the value found in a.
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
    def load_table(cls, db) -> list[Any]:
        """
        Load an entire table from a database.
        """
        logger.debug(f"Reading entire {cls.__name__} table.")
        db.cursor.execute(f"SELECT * FROM {cls.table_name}")
        return db.cursor.fetchall()
    
    def save(self, row:tuple) -> int:
        """
        Add a row to the table.
        """
        a_id = row[0]
        b_id = row[1]
        
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