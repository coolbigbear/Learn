import aiosqlite, asyncio

async def main():
    async with aiosqlite.connect('tutorials.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT id, slug, title, test_cases FROM exercises ORDER BY id') as cur:
            rows = await cur.fetchall()
            for r in rows:
                print(f'ID={r["id"]}, slug={r["slug"]}, title={r["title"]}')
                print(f'  test_cases={r["test_cases"]}')
                print()

asyncio.run(main())
