"""Diagnostic test to verify what run_code returns for Exercise 1 starter code."""
import asyncio
import json
import sys
sys.path.insert(0, '.')
from app.services.exercise_runner import run_code

async def test():
    # Simulate submitting starter code (just a comment) for Exercise 1
    result = await run_code('# Print Hello, World!\n', [
        {'input': '', 'expected_output': 'Hello, World!\n', 'comparison_type': 'exact'}
    ])
    print(json.dumps(result, indent=2, default=str))

asyncio.run(test())
