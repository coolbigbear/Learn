"""Test pandas and fastapi import in the Docker sandbox image."""
import subprocess

for pkg in ['pandas', 'fastapi', 'pydantic']:
    result = subprocess.run(
        ['docker', 'run', '--rm', 'tutorial-runner-python:latest',
         'python3', '-c', f'import {pkg}; print("{pkg} version:", {pkg}.__version__)'],
        capture_output=True, text=True, timeout=15
    )
    stdout = result.stdout.strip()
    stderr = result.stderr.strip().split('\n')[-1] if result.stderr.strip() else ''
    print(f'{pkg}: {stdout or stderr[:120]}')
