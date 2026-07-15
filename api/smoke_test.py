"""Quick smoke test of run_code."""
import sys
sys.path.insert(0, '.')
import asyncio

async def go():
    from app.services.exercise_runner import run_code
    r = await run_code('print(1)', [{'input': '', 'expected_output': '1\n', 'comparison_type': 'exact'}])
    print('Result:', r)

asyncio.run(go())