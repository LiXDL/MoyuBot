import sqlite3

conn = sqlite3.connect('Card.db', isolation_level='IMMEDIATE')
cur = conn.cursor()

cur.execute('''PRAGMA FOREIGN_KEYS = ON''')
conn.commit()

create_info_table = '''
CREATE TABLE IF NOT EXISTS CardInfo
(id INTEGER PRIMARY KEY, 
name TEXT, 
release INTEGER, 
char_id INTEGER, 
school_id INTEGER, 
rarity INTEGER, 
class INTEGER, 
attack_type INTEGER, 
role TEXT, 
position INTEGER, 
total INTEGER, 
speed INTEGER, 
attack INTEGER, 
health INTEGER, 
magic_def INTEGER, 
physical_def INTEGER, 
critical_chance INTEGER, 
critical_damage INTEGER);
'''

create_alias_table = '''
CREATE TABLE IF NOT EXISTS CardAlias
(ca_id INTEGER PRIMARY KEY AUTOINCREMENT, 
card_id INTEGER NOT NULL, 
card_alias TEXT NOT NULL, 
FOREIGN KEY(card_id) REFERENCES CardInfo(id) ON DELETE CASCADE ON UPDATE CASCADE);
'''

cur.execute(create_info_table)
conn.commit()
cur.execute(create_alias_table)
conn.commit()
conn.close()
