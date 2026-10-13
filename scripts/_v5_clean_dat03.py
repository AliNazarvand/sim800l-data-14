import re, yaml
from pathlib import Path

toc_re = re.compile(r'\.{6,}|\.{3,}\d+\s*$')
page_re = re.compile(r'\.{2,}\s*\d+\s*$')

def bad(rec):
    q = (rec.get('source') or {}).get('quote') or ''
    if not q: return False
    if toc_re.search(q): return True
    if page_re.search(q): return True
    if len(q) > 20 and q.count('.') > len(q) * 0.4: return True
    return False

p = Path('data/dat_03_error_code.yaml')
data = yaml.safe_load(p.read_text(encoding='utf-8')) or []
before = len(data)
kept = [r for r in data if not bad(r)]
for i, r in enumerate(kept, 1):
    r['id'] = f'dat_03_{i:04d}'
with open(p, 'w', encoding='utf-8') as f:
    yaml.safe_dump(kept, f, allow_unicode=True, sort_keys=False)
print(f"  dat_03: {before} -> {len(kept)}")