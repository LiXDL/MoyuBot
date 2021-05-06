import sqlite3

conn = sqlite3.connect('Card.db', isolation_level='IMMEDIATE')
cur = conn.cursor()

cur.execute('SELECT * FROM CardInfo;')

print(cur.fetchall())
