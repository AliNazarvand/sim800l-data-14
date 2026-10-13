import re, yaml
from pathlib import Path

toc_re = re.compile(r'\.{6,}|\.{3,}\d+\s*$')
page_re = re.compile(r'\.{2,}\s*\d+\s*$')

def numeric(rec):
    for k in ('value_min','value_typ','value_max'):
        v = rec.get(k)
        if isinstance(v,(int,float)):
            return True
    return False

def sleep_or_power_real(rec):
    p = (rec.get('parameter') or '').lower()
    # Real sleep/power entries should mention sleep mode or specific currents
    for kw in ('sleep mode 1','sleep mode 2','wake up','rtc backup','power down mode'):
        if kw in p: return True
    return False

def is_bad(rec):
    q = (rec.get('source') or {}).get('quote') or ''
    if toc_re.search(q): return True
    if page_re.search(q): return True
    if len(q) > 20 and q.count('.') > len(q) * 0.4: return True
    if '(cid:' in q and not numeric(rec) and not sleep_or_power_real(rec):
        return True
    return False

p = Path('data/dat_15_power_management.yaml')
data = yaml.safe_load(p.read_text(encoding='utf-8')) or []
before = len(data)
kept = []
for r in data:
    if is_bad(r): continue
    if numeric(r) or sleep_or_power_real(r):
        kept.append(r)
for i, r in enumerate(kept, 1):
    r['id'] = f'dat_15_{i:04d}'
with open(p, 'w', encoding='utf-8') as f:
    yaml.safe_dump(kept, f, allow_unicode=True, sort_keys=False)
print(f"  dat_15: {before} -> {len(kept)}")