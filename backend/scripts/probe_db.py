import sqlite3
import pprint

def probe():
    conn = sqlite3.connect('C:/xampp/htdocs/3F/futuroforbes.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in c.fetchall()]
    
    for table in tables:
        print(f"\n--- TABLE: {table} ---")
        c.execute(f"PRAGMA table_info({table})")
        cols = [r['name'] for r in c.fetchall()]
        print("Columns:", ", ".join(cols))

if __name__ == '__main__':
    probe()
