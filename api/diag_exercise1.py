#!/usr/bin/env python3
"""Reproduce the exercise 1 lazy submit bug."""
import asyncio
import json
from app.services.exercise_runner import run_code


async def main():
    # Simulate the lazy submit: just a comment, no print
    result = await run_code("# Print Hello, World!\n", [
        {"input": "", "expected_output": "Hello, World!\n", "comparison_type": "exact"},
    ])
    print(json.dumps(result, indent=2))

    print("\n--- Individual test result ---")
    if result.get("test_results"):
        tr = result["test_results"][0]
        print(f"  passed: {tr.get('passed')}")
        print(f"  expected_output: {tr.get('expected_output')!r}")
        print(f"  actual_output: {tr.get('actual_output')!r}")
        print(f"  message: {tr.get('message')}")

asyncio.run(main())