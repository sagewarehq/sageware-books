"""Build overrides/static/sageware/icons.svg, a sprite of the Lucide icons we use.

Same set and version as Talaria (lucide 0.548.0). Add a name to ICONS and rerun.
"""

import re
import urllib.request
from pathlib import Path

VERSION = "0.548.0"
ICONS = [
    "library-big", "search", "upload", "list-checks", "settings", "circle-user", "log-out", "log-in", "user-plus",
    "book-open", "flame", "download", "star", "book-check", "book-dashed", "shuffle", "tag", "layers", "users",
    "building-2", "languages", "star-half", "file-type", "archive", "table", "info", "bookmark", "plus",
    "chevron-down", "mail", "database", "sliders-horizontal", "palette", "clock", "file-text", "refresh-cw",
    "power", "rotate-ccw", "package", "user-cog", "check", "x", "shield", "hard-drive", "pencil", "arrow-up-circle",
    "send", "headphones", "chevron-left", "external-link", "link", "calendar", "building", "globe", "hash", "book-marked",
    "grip-vertical", "ellipsis", "arrow-up-down", "trash-2", "globe-lock", "lock",
]
OUT = Path(__file__).resolve().parent.parent / "overrides/static/sageware/icons.svg"

symbols = []
for name in ICONS:
    url = f"https://cdn.jsdelivr.net/npm/lucide-static@{VERSION}/icons/{name}.svg"
    svg = urllib.request.urlopen(url).read().decode()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1).strip()
    inner = re.sub(r"\s*\n\s*", "", inner)
    symbols.append(f'<symbol id="{name}" viewBox="0 0 24 24">{inner}</symbol>')

OUT.write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round">\n' + "\n".join(symbols) + "\n</svg>\n"
)
print(f"wrote {len(symbols)} icons to {OUT}")
