from passlib.context import CryptContext
import sqlite3

ctx = CryptContext(schemes=['bcrypt'])
h = ctx.hash('test1234')
conn = sqlite3.connect('3f_app.db')
conn.execute('UPDATE users SET hashed_password=? WHERE email=?', (h, 'fer@3f.com'))
conn.commit()
print('Password updated. Hash prefix:', h[:20])
conn.close()
