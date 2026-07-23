#!/usr/bin/env python3
"""API-based verification of lessons 16-20 exercises."""
import urllib.request, json, sys

token = open('/tmp/reviewer_token.txt').read().strip()
base = 'http://localhost:8081'

def api_get(path):
    req = urllib.request.Request(f'{base}{path}', headers={'Authorization': f'Bearer {token}'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())

# Get all lessons
lessons = api_get('/api/lessons')['lessons']

# Filter lessons 16-20
target_lessons = [l for l in lessons if l['id'] in (16, 17, 18, 19, 20)]
print('=== Lessons 16-20 from API ===')
for l in target_lessons:
    print(f'  id={l["id"]}, slug={l["slug"]}, title="{l["title"]}", path="{l["path"]}", exercises={l["exercise_count"]}')

# Check each lesson's exercises via slug
for l in target_lessons:
    slug = l['slug']
    print(f'\n--- {l["id"]}: {slug} ({l["title"]}) ---')
    try:
        detail = api_get(f'/api/lessons/{slug}')
        ex_list = detail.get('exercises', [])
        print(f'  Exercises in detail: {len(ex_list)}')
        for ex in ex_list:
            print(f'  [{ex["order"]}] id={ex["id"]}, slug="{ex["slug"]}", title="{ex["title"]}"')
            print(f'      instruction: {ex["instruction"][:100]}...')
            print(f'      starter: {"yes" if ex.get("starter_code") else "no"}')
            
            # Also check via exercises endpoint
            ex_detail = api_get(f'/api/exercises/{ex["id"]}')
            print(f'      via /exercises/{ex["id"]}: title="{ex_detail["title"]}", starter={"yes" if ex_detail.get("starter_code") else "no"}')
    except Exception as e:
        print(f'  ERROR: {e}')

print('\n✅ API verification complete')
