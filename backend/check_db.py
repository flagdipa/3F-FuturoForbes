import sqlite3
conn = sqlite3.connect('c:/xampp/htdocs/3F/backend/futuroforbes.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
for row in c.fetchall():
    print(row[0])
