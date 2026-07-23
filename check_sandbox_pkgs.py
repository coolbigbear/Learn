"""Check what packages are available in the Docker sandbox image."""
import subprocess
import json

result = subprocess.run(
    ['docker', 'run', '--rm', 'tutorial-runner-python:latest',
     'python3', '-c', 'import fastapi; print("fastapi:", fastapi.__version__)'],
    capture_output=True, text=True, timeout=15
)
print('fastapi check:', result.stdout.strip(), result.stderr.strip()[:100])

result = subprocess.run(
    ['docker', 'run', '--rm', 'tutorial-runner-python:latest',
     'python3', '-c', 'import pandas; print("pandas:", pandas.__version__)'],
    capture_output=True, text=True, timeout=15
)
print('pandas check:', result.stdout.strip(), result.stderr.strip()[:100])

result = subprocess.run(
    ['docker', 'run', '--rm', 'tutorial-runner-python:latest',
     'python3', '-c', 'import pydantic; print("pydantic:", pydantic.__version__)'],
    capture_output=True, text=True, timeout=15
)
print('pydantic check:', result.stdout.strip(), result.stderr.strip()[:100])
