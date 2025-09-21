import sqlite3
from contextlib import contextmanager

DB_PATH = "finance.db"

SCHEMA = '''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    t_date TEXT NOT NULL,           -- YYYY-MM-DD
    amount REAL NOT NULL,           -- +income, -expense
    category TEXT NOT NULL,
    description TEXT
);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions (t_date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions (category);
'''

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)
        conn.commit()

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()