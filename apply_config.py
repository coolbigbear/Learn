"""Apply config change inside QA container and restart."""
import subprocess

# Patch config.py inside container
result = subprocess.run(
    ['docker', 'exec', 'python-tutorials-qa', 'sed', '-i', 's/MAX_MEMORY_MB = 128/MAX_MEMORY_MB = 512/', '/app/app/config.py'],
    capture_output=True, text=True, timeout=10
)
print('Patch:', result.stdout, result.stderr[:200] if result.stderr else '')

# Verify
result = subprocess.run(
    ['docker', 'exec', 'python-tutorials-qa', 'grep', 'MAX_MEMORY_MB', '/app/app/config.py'],
    capture_output=True, text=True, timeout=10
)
print('Verify:', result.stdout.strip())

# Restart the uvicorn process inside the container
result = subprocess.run(
    ['docker', 'exec', 'python-tutorials-qa', 'pkill', '-HUP', 'uvicorn'],
    capture_output=True, text=True, timeout=10
)
print('Restart:', result.stdout, result.stderr[:200] if result.stderr else '')

# Wait and check health
import time
time.sleep(3)

import urllib.request
try:
    resp = urllib.request.urlopen('http://localhost:8081/api/health', timeout=5)
    print(f'Health: {resp.status}')
except Exception as e:
    print(f'Health check failed: {e}')
