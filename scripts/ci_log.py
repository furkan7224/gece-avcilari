#!/usr/bin/env python3
"""Çalışma günlüğünü ci-logs dalına yazar (GitHub contents API)."""
import os, sys, json, base64, urllib.request
repo, tok = os.environ['GITHUB_REPOSITORY'], os.environ['GH_TOKEN']
slug, run, status = os.environ.get('SLUG', 'job'), os.environ.get('GITHUB_RUN_NUMBER', '0'), os.environ.get('JOB_STATUS', '?')
p = os.path.join(os.environ.get('RUNNER_TEMP', '/tmp'), 'log.txt')
txt = open(p, errors='replace').read()[-300000:] if os.path.exists(p) else '(günlük yok)'
for k in ("KID", "ISS", "TID"):
    v = (os.environ.get(k) or "").strip()
    if v: txt = txt.replace(v, '***')
steps = os.environ.get('STEPS', '{}')
try: steps = json.dumps({k: v.get('outcome') for k, v in json.loads(steps).items()}, ensure_ascii=False)
except Exception: pass
body = f"durum: {status}\nadımlar: {steps}\n-----\n{txt}".encode()
def api(method, path, data=None):
    r = urllib.request.Request(f'https://api.github.com/repos/{repo}/contents/{path}', method=method,
        data=json.dumps(data).encode() if data else None,
        headers={'Authorization': 'Bearer ' + tok, 'Accept': 'application/vnd.github+json'})
    try:
        with urllib.request.urlopen(r) as x: return json.load(x)
    except urllib.error.HTTPError as e:
        if e.code != 404: print('günlük hatası', e.code, e.read()[:300])
        return None
for path in (f'{slug}-{run}.txt', f'son-{slug}.txt'):
    cur = api('GET', path + '?ref=ci-logs')
    d = {'message': f'günlük {slug} {run}', 'content': base64.b64encode(body).decode(), 'branch': 'ci-logs'}
    if cur and 'sha' in cur: d['sha'] = cur['sha']
    print(path, 'yazıldı' if api('PUT', path, d) else 'YAZILAMADI')
