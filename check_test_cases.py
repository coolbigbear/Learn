"""Get exercise test cases via API."""
import json, urllib.request

token = open('/tmp/reviewer_token.txt').read().strip()
base = 'http://localhost:8081'

def get(path):
    req = urllib.request.Request(f'{base}{path}', headers={'Authorization': f'Bearer {token}'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

for ex_id in [60, 70, 80, 88, 91]:
    ex = get(f'/api/exercises/{ex_id}')
    print(f'=== Exercise {ex_id}: {ex.get("title","?")} ===')
    tcs = ex.get('test_cases', [])
    if tcs:
        for i, tc in enumerate(tcs):
            print(f'  [{i}] type={tc.get("comparison_type")}, name={tc.get("name")}')
            print(f'      expected={repr(tc.get("expected_output",""))[:120]}')
            print(f'      input={repr(tc.get("input",""))[:60]}')
            print(f'      message={tc.get("message","")[:80]}')
    else:
        print(f'  No test cases')
    print()
