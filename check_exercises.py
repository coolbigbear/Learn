#!/usr/bin/env python3
import json, os

content_dir = os.path.join(os.path.dirname(__file__), 'content')
lessons_to_check = ['16-csv-processing', '17-json-processing', '18-data-processing-libraries', '19-fastapi-intro', '20-mini-api-project']

for slug in lessons_to_check:
    ex_path = os.path.join(content_dir, slug, 'exercises.json')
    with open(ex_path) as f:
        exercises = json.load(f)
    print(f'{slug} ({slug.split("-",1)[1]}): {len(exercises)} exercises')
    for ex in exercises:
        print(f'  Exercise {ex["order"]}: {ex["slug"]} - {ex["title"]}')
    print()
