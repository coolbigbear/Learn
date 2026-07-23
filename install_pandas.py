"""Install pandas in the QA container."""
import subprocess

result = subprocess.run(
    ['docker', 'exec', 'python-tutorials-qa', 'pip', 'install', 'pandas'],
    capture_output=True, text=True, timeout=60
)
print(result.stdout[-300:] if result.stdout else '')
if result.stderr:
    print('STDERR:', result.stderr[:200])
print('Exit:', result.returncode)
