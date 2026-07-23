"""Check test cases in the database."""
import sqlite3
import json

db = sqlite3.connect('api/data/tutorials.db')
cur = db.cursor()

for ex_id in [60, 70, 80, 88, 91]:
    cur.execute('SELECT id, title, slug, solution_code, test_cases FROM exercises WHERE id=?', (ex_id,))
    row = cur.fetchone()
    if row:
        print(f'--- Ex {row[0]}: {row[1]} ({row[2]}) ---')
        print(f'  solution: {repr(row[3])[:300]}')
        try:
            tc = json.loads(row[4])
            print(f'  test_cases count: {len(tc)}')
            for i, t in enumerate(tc):
                print(f'    [{i}] type={t.get("comparison_type")}, input={repr(t.get("input",""))[:60]}, expected={repr(t.get("expected_output",""))[:100]}, name={t.get("name")}')
        except:
            print(f'  raw test_cases: {row[4][:300]}')
        print()

db.close()
