import sqlite3
import os
from flask import g

DATABASE = os.path.join(os.path.dirname(__file__), 'students.db')

def get_db_connection():
    """Returns a standalone database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys support in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def get_db():
    """Gets the database connection for the Flask application context."""
    if 'db' not in g:
        g.db = get_db_connection()
    return g.db

def close_db(e=None):
    """Closes the database connection if it exists in Flask application context."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(force_seed=False):
    """Initializes the database using schema.sql and optionally seeds it."""
    db = get_db_connection()
    
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    seed_path = os.path.join(os.path.dirname(__file__), 'seed.sql')
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())
        
    db.commit()
    
    # Run seed if force_seed is true or if table is empty
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]
    
    if force_seed or count == 0:
        if os.path.exists(seed_path):
            with open(seed_path, 'r', encoding='utf-8') as f:
                db.executescript(f.read())
            db.commit()
            
    db.close()

def query_db(query, args=(), one=False):
    """Executes a query and returns results as dicts."""
    db = get_db() if g else get_db_connection()
    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    
    # Close standalone connection if not in Flask context
    if not g:
        db.commit()
        db.close()
        
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Executes an INSERT, UPDATE, or DELETE query and returns the lastrowid or affected rows."""
    db = get_db() if g else get_db_connection()
    cur = db.execute(query, args)
    lastrowid = cur.lastrowid
    
    # In Flask context we commit but don't close (Flask closes at request end)
    if g:
        db.commit()
    else:
        db.commit()
        db.close()
        
    cur.close()
    return lastrowid
