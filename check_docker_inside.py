"""Check Docker status inside the QA container."""
import subprocess, json

result = subprocess.run(
    ['docker', 'exec', 'python-tutorials-qa', 'python3', '-c', '''
import docker
client = docker.from_env()
try:
    client.ping()
    print("Docker daemon: REACHABLE")
    images = [i.tags for i in client.images.list() if "tutorial-runner-python" in str(i.tags)]
    print(f"Sandbox images: {images}")
except Exception as e:
    print(f"Docker daemon: UNREACHABLE ({e})")
'''],
    capture_output=True, text=True, timeout=15
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[:200])
