"""Check Docker availability inside QA container."""
import subprocess, json

code = '''
import docker
client = docker.from_env()
try:
    client.ping()
    print("Docker: REACHABLE")
    containers = client.containers.list(all=True, filters={"ancestor": "tutorial-runner-python"})
    print(f"Leaked containers: {len(containers)}")
    for c in containers:
        print(f"  {c.id[:12]} status={c.status}")
except Exception as e:
    print(f"Docker error: {e}")
'''

result = subprocess.run(
    ['docker', 'exec', 'python-tutorials-qa', 'python3', '-c', code],
    capture_output=True, text=True, timeout=15
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[:300])
