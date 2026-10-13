import re, yaml
from pathlib import Path

def valid(rec):
    u = (rec.get('urc_string') or '').strip()
    if not u: return False
    # URCs start with + or are RING/NO CARRIER/ERROR etc.
    if not (u.startswith('+') or u in ('RING','NO CARRIER','ERROR','OK','BUSY')):
        # allow +SAPBR etc
        if not re.match(r'^\+[A-Z0-9_]{2,}$', u):
            return False
    # parameters must be a list of dicts with at least a name
    ps = rec.get('parameters') or []
    for p in ps:
        if not isinstance(p, dict): return False
        if not (p.get('name') or '').strip(): return False
    return True

p = Path('data/dat_02_urc.yaml')
data = yaml.safe_load(p.read_text(encoding='utf-8')) or []
before = len(data)
kept = [r for r in data if valid(r)]
for i, r in enumerate(kept, 1):
    r['id'] = f'dat_02_{i:04d}'
with open(p, 'w', encoding='utf-8') as f:
    yaml.safe_dump(kept, f, allow_unicode=True, sort_keys=False)
print(f"  dat_02: {before} -> {len(kept)}")