"""Test repr behavior in template formatting."""
import textwrap

# Simulate what HARNESS_TEMPLATE.format does
user_code = "# Print Hello, World!\n"
test_cases = [{'input': '', 'expected_output': 'Hello, World!\n', 'comparison_type': 'exact'}]

# Test repr directly
print("repr(user_code):", repr(user_code))
print("repr(test_cases):", repr(test_cases))

# Simulate what the harness would receive
eval_code = f"_USER_CODE = {user_code!r}\n_TEST_CASES = {test_cases!r}"
print("\n--- Generated Python code ---")
print(eval_code)
print("---")

# Execute the generated code to see what values we get
local_vars = {}
exec(eval_code, {}, local_vars)
print(f"\n_USER_CODE = {local_vars['_USER_CODE']!r}")
print(f"_TEST_CASES[0]['expected_output'] = {local_vars['_TEST_CASES'][0]['expected_output']!r}")

# Check if expected_output has a real newline
expected = local_vars['_TEST_CASES'][0]['expected_output']
print(f"\nIs newline present: {chr(10) in expected}")
print(f"Length: {len(expected)}")
print(f"repr: {repr(expected)}")
