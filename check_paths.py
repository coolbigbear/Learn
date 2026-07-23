#!/usr/bin/env python3
import urllib.request, json

token = open('/tmp/reviewer_token.txt').read().strip()
base = 'http://localhost:8081'

req = urllib.request.Request(f'{base}/api/lessons/by-path', headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read())

print("=== Path groups from API ===")
for path in data.get('paths', []):
    print(f"\n{path['display_name']} ({path['path']})")
    print(f"  Color: {path.get('color')}")
    print(f"  Description: {path.get('description')}")
    print(f"  Lessons ({len(path.get('lessons', []))}):")
    for l in path['lessons']:
        print(f"    {l['order']}. {l['title']} ({l['exercise_count']} ex)")
