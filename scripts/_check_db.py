#!/usr/bin/env python3
"""Check current DB state for random-data exercise."""
import sqlite3, json

conn = sqlite3.connect('/app/data/tutorials.db')
row = conn.execute("SELECT slug, test_cases FROM exercises WHERE slug='random-data'").fetchone()
if row:
    tc = json.loads(row[1])
    print('Slug:', row[0])
    print('Current expected_output:', repr(tc[0].get('expected_output', 'N/A')))
else:
    print('Exercise not found')
conn.close()
