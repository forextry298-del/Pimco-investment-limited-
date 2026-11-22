#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")"
ROOT="$(pwd)"
[ -f app.py ] && [ -d templates ] || { echo "Run this from ~/pimco_investment after extracting the ZIP."; exit 1; }
mkdir -p backups
STAMP="$(date +%Y%m%d_%H%M%S)"
for f in templates/equipment.html templates/base.html templates/index.html templates/registered.html; do
  [ -f "$f" ] && cp "$f" "backups/$(basename "$f").cleanup.$STAMP"
done
python - <<'PY'
from pathlib import Path
import re
# Remove the requested header and wallet panel from the product page.
p=Path("templates/equipment.html")
if p.exists():
    s=p.read_text()
    s=re.sub(r'(?s)(\{% block content %\}).*?(?=<div class="pimco-plan-grid">)', r'\1\n', s, count=1)
    s=re.sub(r'(?s)<p class="pimco-note">.*?</p>\s*', '', s)
    s=s.replace("Projected figures are illustrative estimates only and are not guaranteed earnings.", "")
    p.write_text(s)
# Remove the top-left PIMCO brand/platform title block from base template.
p=Path("templates/base.html")
if p.exists():
    s=p.read_text()
    s=re.sub(r'(?s)<div class="brand">.*?</div>\s*</div>', '', s, count=1)
    # Fallback: strip just the exact branding text if markup differs.
    s=re.sub(r'(?i)PIMCO\s*', '', s)
    s=re.sub(r'(?i)INVESTMENT\s+PLATFORM', '', s)
    p.write_text(s)
# Registration/login screens: suppress warning/notice flash banners and remove warning labels.
for name in ("templates/index.html","templates/registered.html"):
    p=Path(name)
    if not p.exists(): continue
    s=p.read_text()
    # Remove flash message blocks on authentication pages, so warning banners are not shown there.
    s=re.sub(r'(?s)\{% with messages = get_flashed_messages.*? \{% endwith %\}', '', s)
    s=re.sub(r'(?is)<[^>]*class=["\'][^"\']*(?:warning|warn|alert)[^"\']*["\'][^>]*>.*?</[^>]+>', '', s)
    s=re.sub(r'(?i)\bwarning\s*:?\s*', '', s)
    p.write_text(s)
# Clean literal slash-n and stray comma/newline artifacts in user-facing template/static text.
for root in ("templates","static"):
    for p in Path(root).rglob("*"):
        if not p.is_file() or p.suffix.lower() not in (".html",".css",".js",".txt",".svg",".json"): continue
        try: s=p.read_text()
        except UnicodeDecodeError: continue
        s=s.replace(r"\n", "").replace(",,\n,,", "").replace(",,\\n,,", "")
        s=s.replace(",,\r\n,,", "")
        p.write_text(s)
print("Removed requested product header/wallet panel, branding, earnings disclaimer, and auth warning banners; cleaned literal \\n.")
PY
python -m py_compile app.py
echo "Cleanup applied. Restart Flask and refresh the site."
