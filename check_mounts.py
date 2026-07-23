#!/usr/bin/env python3
import subprocess, json

r = subprocess.run(['docker', 'inspect', 'python-tutorials-qa', '--format', '{{json .Mounts}}'],
                   capture_output=True, text=True, timeout=10)
if r.stdout:
    mounts = json.loads(r.stdout)
    for m in mounts:
        print(f'{m.get("Source","?")} -> {m.get("Destination","?")} ({m.get("Mode","")})')
else:
    print("No stdout")
    print("Stderr:", r.stderr[:300])

# Also check if docker.sock is accessible
r2 = subprocess.run(['docker', 'exec', 'python-tutorials-qa', 'ls', '-la', '/var/run/docker.sock'],
                    capture_output=True, text=True, timeout=10)
print(f"\nDocker socket: {r2.stdout}{r2.stderr}")
