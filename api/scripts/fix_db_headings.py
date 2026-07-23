import sqlite3

conn = sqlite3.connect('/app/data/tutorials.db')
c = conn.cursor()

# Fix lesson 19
c.execute("UPDATE lessons SET content = replace(content, '# Lesson 17: Introduction to FastAPI', '# Lesson 19: Introduction to FastAPI') WHERE slug = '19-fastapi-intro'")
print('Lesson 19 rows affected:', c.rowcount)

# Fix lesson 20
c.execute("UPDATE lessons SET content = replace(content, '# Lesson 18: Mini API Project', '# Lesson 20: Mini API Project') WHERE slug = '20-mini-api-project'")
print('Lesson 20 rows affected:', c.rowcount)

conn.commit()

# Verify
c.execute("SELECT slug, substr(content, 1, 60) FROM lessons WHERE slug IN ('19-fastapi-intro', '20-mini-api-project')")
for row in c:
    print(row)
conn.close()
