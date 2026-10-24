"""Regenerate the theme mounts in docker-compose.yml and docker-compose.dev.yml.

Both run the stock Calibre-Web image and bind-mount every file in overrides/ on top of it.
Run this after adding or removing a template override.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEGIN, END = "# theme mounts: begin (tools/gen_compose.py)", "# theme mounts: end"


def mounts(indent):
    lines = [f"{indent}- ./overrides/static/sageware:/app/calibre-web/cps/static/sageware:ro"]
    for tpl in sorted((ROOT / "overrides/templates").glob("*.html")):
        lines.append(f"{indent}- ./overrides/templates/{tpl.name}:/app/calibre-web/cps/templates/{tpl.name}:ro")
    return lines


for name in ("docker-compose.yml", "docker-compose.dev.yml"):
    path = ROOT / name
    text = path.read_text()
    match = re.search(rf"^(\s*){re.escape(BEGIN)}\n.*?^\s*{re.escape(END)}$", text, re.M | re.S)
    if not match:
        raise SystemExit(f"{name}: markers not found")
    indent = match.group(1)
    block = "\n".join([indent + BEGIN, *mounts(indent), indent + END])
    path.write_text(text[: match.start()] + block + text[match.end():])
    print(f"{name}: {len(mounts(indent))} mounts")
