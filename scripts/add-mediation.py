#!/usr/bin/env python3
"""cap sync sonrası iOS CapApp-SPM paketine Unity Ads ve Liftoff Monetize aracılık eklentilerini ekler (tekrar çalıştırılabilir)."""
import pathlib
p = pathlib.Path(__file__).resolve().parent.parent / 'ios/App/CapApp-SPM/Package.swift'
s = p.read_text()
PKGS = [
    ('googleads-mobile-ios-mediation-unity', '85ed786e866d6de9cdb30c9059c36d77bcb76af4', 'UnityAdapterTarget'),
    ('googleads-mobile-ios-mediation-liftoffmonetize', '1419a7037b2d18b0b49901edf19b08bdc9297bbf', 'LiftoffMonetizeAdapterTarget'),
]
for repo, rev, prod in PKGS:
    if repo in s:
        continue
    import re
    s = re.sub(r'(\n)([ \t]*)(\.package\(url: "https://github.com/ionic-team)',
               lambda m: f'{m.group(1)}{m.group(2)}.package(url: "https://github.com/googleads/{repo}.git", revision: "{rev}"),\n{m.group(2)}{m.group(3)}', s, count=1)
    s = re.sub(r'(\n)([ \t]*)(\.product\(name: "Capacitor",)',
               lambda m: f'{m.group(1)}{m.group(2)}.product(name: "{prod}", package: "{repo}"),\n{m.group(2)}{m.group(3)}', s, count=1)
    assert repo in s, 'Package.swift biçimi değişmiş'
p.write_text(s)
print('Aracılık eklentileri eklendi:', ', '.join(x[2] for x in PKGS))
