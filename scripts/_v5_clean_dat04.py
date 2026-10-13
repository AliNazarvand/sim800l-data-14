import yaml
from pathlib import Path

TIMING_UNITS = {'ms','us','s','ns','min','hour','h','minute','second'}
def is_timing(rec):
    unit = (rec.get('unit') or '').strip().lower()
    if unit in TIMING_UNITS: return True
    # Some timing records have unit empty but parameter names contain time
    pname = (rec.get('parameter') or '').lower()
    for kw in ('time','delay','wait','pulse','ms','us','durat','timeout'):
        if kw in pname: return True
    return False

p = Path('data/dat_04_timing_timeout.yaml')
data = yaml.safe_load(p.read_text(encoding='utf-8')) or []
before = len(data)
kept = [r for r in data if is_timing(r)]
for i, r in enumerate(kept, 1):
    r['id'] = f'dat_04_{i:04d}'
with open(p, 'w', encoding='utf-8') as f:
    yaml.safe_dump(kept, f, allow_unicode=True, sort_keys=False)
print(f"  dat_04: {before} -> {len(kept)}")