import sqlite3

conn = sqlite3.connect('CompanyRevue.db', isolation_level='IMMEDIATE')
cur = conn.cursor()

cur.execute('''PRAGMA FOREIGN_KEYS = ON''')
conn.commit()

drop_record_table = '''
DROP TABLE IF EXISTS RevueRecord;
'''

drop_team_table = '''
DROP TABLE IF EXISTS Team;
'''

drop_boss_table = '''
DROP TABLE IF EXISTS BossInfo;
'''

drop_company_table = '''
DROP TABLE IF EXISTS CompanyInfo; 
'''

create_company_table = '''
CREATE TABLE IF NOT EXISTS CompanyInfo (
id TEXT PRIMARY KEY, 
alias TEXT, 
account TEXT, 
password TEXT
);
'''

create_boss_table = '''
CREATE TABLE IF NOT EXISTS BossInfo (
id INT PRIMARY KEY, 
alias TEXT, 
health INT
);
'''

create_team_table = '''
CREATE TABLE IF NOT EXISTS Team (
id INTEGER PRIMARY KEY AUTOINCREMENT, 
member_id TEXT, 
char_id TEXT, 
CONSTRAINT fk_member 
FOREIGN KEY (member_id) REFERENCES CompanyInfo(id)
ON UPDATE CASCADE ON DELETE NO ACTION
);
'''

create_record_table = '''
CREATE TABLE IF NOT EXISTS RevueRecord (
id INTEGER PRIMARY KEY AUTOINCREMENT, 
member_id TEXT, 
boss_id INT, 
team INT, 
sequence INT, 
turn INT, 
remain_turn INT, 
damage INT, 
time INT, 
CONSTRAINT fk_member 
FOREIGN KEY (member_id) REFERENCES CompanyInfo(id) 
ON UPDATE CASCADE ON DELETE NO ACTION 
CONSTRAINT fk_boss
FOREIGN KEY (boss_id) REFERENCES BossInfo(id)
ON UPDATE CASCADE ON DELETE NO ACTION
);
'''


cur.execute(drop_record_table)
cur.execute(drop_team_table)
cur.execute(drop_boss_table)
cur.execute(drop_company_table)
conn.commit()

cur.execute(create_company_table)
cur.execute(create_boss_table)
cur.execute(create_team_table)
cur.execute(create_record_table)
conn.commit()

conn.close()
