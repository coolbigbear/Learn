#!/usr/bin/env python3
"""Check container's baked-in content vs local content for random-data."""
import json

# Container content (old, baked in image)
try:
    with open('/app/content/python/21-intro-to-ml/exercises.json') as f:
        container_ex = json.load(f)
    for ex in container_ex:
        if ex['slug'] == 'random-data':
            container_exp = ex['test_cases'][0]['expected_output']
            print('Container (baked-in) expected_output:', repr(container_exp))
            break
except FileNotFoundError:
    print('Container: /app/content/python/21-intro-to-ml/exercises.json NOT FOUND')

# Updated content from sync dir
with open('/app/content-updated/21-intro-to-ml/exercises.json') as f:
    updated_ex = json.load(f)
for ex in updated_ex:
    if ex['slug'] == 'random-data':
        updated_exp = ex['test_cases'][0]['expected_output']
        print('Updated content expected_output:', repr(updated_exp))
        break
