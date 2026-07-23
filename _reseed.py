import asyncio
from app.services.content_seed import seed_content
from app.database import async_session_factory
from sqlalchemy import text

async def reset_and_seed():
    async with async_session_factory() as session:
        await session.execute(text('DELETE FROM user_progress'))
        await session.execute(text('DELETE FROM exercises'))
        await session.execute(text('DELETE FROM lessons'))
        await session.commit()
    
    result = await seed_content()
    print(f'Result: {result}')

asyncio.run(reset_and_seed())
