import sqlite3
import json

db = sqlite3.connect('/opt/data/projects/python-tutorials/api/tutorials.db')
cursor = db.execute('SELECT id, slug, test_cases FROM exercises WHERE id=1')
row = cursor.fetchone()
print(f'id={row[0]}, slug={row[1]}')
tc = json.loads(row[2]) if row[2] else None
print(f'test_cases={tc}')
db.close()
