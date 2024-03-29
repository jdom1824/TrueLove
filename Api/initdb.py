# initdb.py

import sqlite3

# Connection to SQLite database
conn = sqlite3.connect('users.db')
c = conn.cursor()

def initialize_db():
    """Initializes the database by creating the users table if it doesn't exist."""
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            public_key TEXT NOT NULL UNIQUE,
            private_key TEXT NOT NULL
        );
    """)
    conn.commit()