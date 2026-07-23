#!/usr/bin/env python3
"""Verify DB was updated correctly."""
import sqlite3, json

conn = sqlite3.connect('/app/data/tutorials.db')
row = conn.execute("SELECT slug, test_cases FROM exercises WHERE slug='random-data'").fetchone()
if row:
    tc = json.loads(row[1])
    exp = tc[0].get('expected_output', 'N/A')
    print('Slug:', row[0])
    print('Expected output:', repr(exp))
    assert '0.5201' in exp, f"FAIL: expected_output should contain 0.5201, got {exp}"
    assert '0.0581' in exp, f"FAIL: expected_output should contain 0.0581, got {exp}"
    print('VERIFIED: DB has correct numpy 2.x expected_output values')
else:
    print('FAIL: Exercise not found')
conn.close()
