"""Write assets/hud.svg: today's farm date plus repo and contribution counts.

Standard library only, so it runs on a bare Actions runner. The frame and the pixel
glyphs come from template.svg and glyphs.json, which tools/build.py generates.

Usage: GH_TOKEN=... python3 .github/hud/hud.py
       NOW=2026-10-17T20:00 overrides the current UTC time (for testing).
"""
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER = 'Yakou207'
HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / 'assets' / 'hud.svg'
SEASONS = ['Winter', 'Winter', 'Spring', 'Spring', 'Spring', 'Summer',
           'Summer', 'Summer', 'Fall', 'Fall', 'Fall', 'Winter']


def graphql(query):
    req = urllib.request.Request(
        'https://api.github.com/graphql', data=json.dumps({'query': query}).encode(),
        headers={'Authorization': f'bearer {os.environ["GH_TOKEN"]}'})
    with urllib.request.urlopen(req) as r:
        return json.load(r)['data']


def text(atlas, s, x, y, style, align='left'):
    glyphs = atlas['glyphs'][style]
    if align == 'right':
        x -= sum(glyphs[c][0] for c in s)
    out = []
    for c in s:
        adv, rects = glyphs[c]
        out.append(f'<g transform="translate({round(x)},{y})">{rects}</g>')
        x += adv
    return ''.join(out)


def main():
    now = datetime.fromisoformat(os.environ['NOW']).replace(tzinfo=timezone.utc) \
        if os.environ.get('NOW') else datetime.now(timezone.utc)
    user = graphql(f'query{{user(login:"{USER}"){{createdAt repositories(privacy:PUBLIC,ownerAffiliations:OWNER)'
                   f'{{totalCount}} contributionsCollection{{contributionCalendar{{totalContributions}}}}}}}}')['user']
    born = datetime.fromisoformat(user['createdAt'].replace('Z', '+00:00'))
    days = (now.date() - born.date()).days + 1
    year = (days - 1) // 365 + 1
    repos = user['repositories']['totalCount']
    harvest = user['contributionsCollection']['contributionCalendar']['totalContributions']

    atlas = json.loads((HERE / 'glyphs.json').read_text())
    scene = 'day' if 6 <= now.hour < 18 else 'night'
    parts = [
        atlas['icons'][scene],
        text(atlas, f'{now:%a}. {now.day}', 224, 34, 'big'),
        text(atlas, f'{SEASONS[now.month - 1]} · Year {year}', 226, 84, 'small'),
        text(atlas, f'Day {days} on the farm', 226, 112, 'small'),
        text(atlas, 'Repos planted', 486, 44, 'label'),
        text(atlas, str(repos), 696, 34, 'big', 'right'),
        text(atlas, 'Harvest', 486, 104, 'label'),
        text(atlas, 'contributions, past year', 486, 126, 'small'),
        text(atlas, str(harvest), 696, 94, 'big', 'right'),
    ]
    template = (HERE / 'template.svg').read_text()
    OUT.write_text(template.replace('<!--DYNAMIC-->', ''.join(parts)))
    print(f'{now:%a}. {now.day} {SEASONS[now.month - 1]} Y{year} day {days} {scene}; '
          f'repos {repos}, harvest {harvest}')


if __name__ == '__main__':
    main()
