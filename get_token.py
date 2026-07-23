#!/usr/bin/env python3
import subprocess, json

result = subprocess.run([
    'curl', '-s', '-X', 'POST', 'https://pi2.tail8c7cb.ts.net/api/auth/login',
    '-H', 'Content-Type: application/json',
    '-d', '{"username":"reviewer","password":"devprofile"}'
], capture_output=True, text=True)
data = json.loads(result.stdout)
token = data['token']
with open('/tmp/reviewer_token.txt', 'w') as f:
    f.write(token)
print(f'Token saved: {len(token)} chars')
print(f'First 20: {token[:20]}...')
