#!/usr/bin/env python3
import subprocess, sys
# Check if docker Python SDK is available in the QA container
r = subprocess.run(['docker', 'exec', 'python-tutorials-qa', 'python3', '-c', 'import docker; print("Docker SDK:", docker.__version__)'], 
                   capture_output=True, text=True, timeout=10)
print("STDOUT:", r.stdout)
print("STDERR:", r.stderr)
print("RC:", r.returncode)
