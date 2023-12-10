from dataclasses import dataclass
import sqlite3

@dataclass
class DBCfg():
    """Database configuration object.
    
    User-defined parameters:
    :db: the database location.
    """
    db: str = "./db/test.db"
    conn = sqlite3.connect(db)
    cursor = conn.cursor()