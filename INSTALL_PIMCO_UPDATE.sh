#!/data/data/com.termux/files/usr/bin/bash
set -e
ROOT="$(pwd)"
if [ ! -f "$ROOT/app.py" ] || [ ! -d "$ROOT/templates" ] || [ ! -d "$ROOT/static" ]; then
  echo "Run this from your ~/pimco_investment project folder."
  exit 1
fi
mkdir -p backups
STAMP="$(date +%Y%m%d_%H%M%S)"
cp templates/home.html "backups/home.html.$STAMP" 2>/dev/null || true
cp templates/base.html "backups/base.html.$STAMP" 2>/dev/null || true
cp static/style.css "backups/style.css.$STAMP" 2>/dev/null || true
# Install files included beside this script in the archive
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p static/product-images
# Images are already extracted into static/product-images/
python - <<'PY'
from pathlib import Path
import re
home=Path("templates/home.html")
s=home.read_text()
include='{% include "home_image_slider.html" %}'
# Replace the existing hero artwork/animation with the image-based auto slider.
s,n=re.subn(r'<section class="hero">.*?</section>', include, s, count=1, flags=re.S)
if not n and include not in s:
    s=s.replace('{% block content %}', '{% block content %}\n'+include, 1)
home.write_text(s)
# Attach the slider stylesheet to base template if it isn't already loaded.
base=Path("templates/base.html")
if base.exists():
    b=base.read_text()
    link="<link rel=\"stylesheet\" href=\"{{ url_for('static', filename='home-slider.css') }}\">"
    if 'home-slider.css' not in b:
        if '</head>' in b: b=b.replace('</head>', '  '+link+'\n</head>', 1)
        else: b += '\n'+link+'\n'
    base.write_text(b)
# Remove visible "demo" wording throughout app templates and static text; keep the app's notification helper working.
for root in ("templates","static"):
    for p in Path(root).rglob("*"):
        if not p.is_file() or p.suffix.lower() not in (".html",".css",".js",".txt",".json",".svg"):
            continue
        try: t=p.read_text()
        except UnicodeDecodeError: continue
        t=re.sub(r'(?i)\bdemoAlert\b', 'notifyUser', t)
        t=re.sub(r'(?i)\bdemo\b', '', t)
        # Remove the stray upper-left punctuation/newline artifact.
        t=t.replace(',,\n,,','').replace(',,\\n,,','')
        t=t.replace(',,\r\n,,','')
        p.write_text(t)
# Also remove that artifact from the README if present.
p=Path("README.md")
if p.exists():
    t=p.read_text()
    t=re.sub(r'(?i)\bdemo\b','',t).replace(',,\n,,','').replace(',,\\n,,','')
    p.write_text(t)
print("Installed image auto-slider and cleaned visible demo/artifact text.")
PY
echo "Done. Restart Flask and open http://127.0.0.1:5000/"
