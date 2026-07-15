"""Quick verification of comment_contains comparison type via run_code."""
import sys
import asyncio
import traceback

sys.path.insert(0, '.')

async def main():
    from app.services.exercise_runner import run_code

    print("Running test 1: comment_contains passes when comment has expected text")
    result = await run_code('# This program prints numbers\nprint(10)', [
        {'input': '', 'expected_output': '# This program prints numbers', 'comparison_type': 'comment_contains'},
    ])
    assert result['passed'], f"FAILED: {result}"
    assert result['test_results'][0]['passed'], f"FAILED sub-result: {result}"
    print('PASS')

    print("Running test 2: comment_contains fails when expected text not in comment")
    result = await run_code('# Wrong comment\nprint(10)', [
        {'input': '', 'expected_output': '# This program prints numbers', 'comparison_type': 'comment_contains'},
    ])
    assert not result['passed'], f"FAILED: {result}"
    assert not result['test_results'][0]['passed'], f"FAILED sub-result: {result}"
    print('PASS')

    print("Running test 3: comment_contains fails when no comment at all")
    result = await run_code('print("hello")', [
        {'input': '', 'expected_output': '# Some comment', 'comparison_type': 'comment_contains'},
    ])
    assert not result['passed'], f"FAILED: {result}"
    assert not result['test_results'][0]['passed'], f"FAILED sub-result: {result}"
    print('PASS')

    print("Running test 4: comment_contains fails when text only in string literal")
    result = await run_code('x = "# This program prints numbers"\nprint(x)', [
        {'input': '', 'expected_output': '# This program prints numbers', 'comparison_type': 'comment_contains'},
    ])
    assert not result['passed'], f"FAILED: {result}"
    assert not result['test_results'][0]['passed'], f"FAILED sub-result: {result}"
    print('PASS')

    print("Running test 5: original comment type still works")
    result = await run_code('# still a comment\nprint(10)', [
        {'input': '', 'expected_output': '', 'comparison_type': 'comment'},
    ])
    assert result['passed'], f"FAILED: {result}"
    print('PASS')

    print("Running test 6: comment_contains passes with inline comment")
    result = await run_code('print("Hi there!")  # Prints a greeting', [
        {'input': '', 'expected_output': '# Prints a greeting', 'comparison_type': 'comment_contains'},
    ])
    assert result['passed'], f"FAILED: {result}"
    print('PASS')

    print("Running test 7: Ex14 starter code fails comment_contains")
    result = await run_code('# Write your comment here\n', [
        {'input': '', 'expected_output': '# Tell the user Python is fun', 'comparison_type': 'comment_contains'},
    ])
    assert not result['passed'], f"FAILED: {result}"
    print('PASS')

    print("Running test 8: Ex14 solution code passes")
    result = await run_code('# Tell the user Python is fun\nprint("Learning Python is fun!")', [
        {'input': '', 'expected_output': '# Tell the user Python is fun', 'comparison_type': 'comment_contains'},
    ])
    assert result['passed'], f"FAILED: {result}"
    print('PASS')

    print("Running test 9: Ex15 confused student (wrong TODO) fails")
    result = await run_code('# TODO: Fix bugs\nprint("Hello, world!")', [
        {'input': '', 'expected_output': '# TODO: Add more features later', 'comparison_type': 'comment_contains'},
    ])
    assert not result['passed'], f"FAILED: {result}"
    print('PASS')

    print('\n=== ALL TESTS PASSED ===')

try:
    asyncio.run(main())
except Exception as e:
    traceback.print_exc()
    sys.exit(1)