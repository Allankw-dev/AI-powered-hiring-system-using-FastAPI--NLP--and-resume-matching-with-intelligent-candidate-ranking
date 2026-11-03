"""Regenerate THIRD_PARTY_NOTICES.md (licences of every package the backend needs + the fonts).

    pip install -r requirements-dev.txt
    python -m scripts.generate_notices
"""
import importlib.metadata as md
import json
import re
import subprocess  # nosec B404
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
OUT = BACKEND.parent / "THIRD_PARTY_NOTICES.md"

FRONTEND = [
    ("Streamlit", "Apache-2.0", "https://streamlit.io"),
    ("requests", "Apache-2.0", "https://requests.readthedocs.io"),
]
FONTS = [
    ("Orbitron", "Matt McInerney", "SIL Open Font License 1.1", "https://fonts.google.com/specimen/Orbitron"),
    ("Exo 2", "Natanael Gama", "SIL Open Font License 1.1", "https://fonts.google.com/specimen/Exo+2"),
]


def requirement_names() -> list[str]:
    names = []
    for line in (BACKEND / "requirements.txt").read_text().splitlines():
        line = line.split("#")[0].strip()
        if line:
            names.append(re.split(r"[~=<>!\[ ]", line)[0].lower().replace("_", "-"))
    return names


def closure(roots: list[str]) -> list[str]:
    seen, stack = set(), list(roots)
    while stack:
        name = stack.pop()
        if name in seen:
            continue
        try:
            dist = md.distribution(name)
        except md.PackageNotFoundError:
            continue
        seen.add(name)
        for req in dist.requires or []:
            if "extra ==" in req:
                continue
            m = re.match(r"[A-Za-z0-9_.-]+", req)
            if m:
                stack.append(m.group(0).lower().replace("_", "-"))
    return sorted(seen)


def main() -> int:
    packages = closure(requirement_names())
    raw = subprocess.run(  # nosec B603
        [sys.executable, "-m", "piplicenses", "--format=json", "--with-urls", "--packages", *packages],
        capture_output=True, text=True, check=True,
    ).stdout
    rows = sorted(json.loads(raw), key=lambda r: r["Name"].lower())

    lines = [
        "# Third-party notices", "",
        "AI Hiring System is built on open-source software and open fonts. Thank you to their authors.",
        "This file lists what is used and under which licence. Regenerate it with `python -m scripts.generate_notices`.", "",
        "## Fonts", "",
        "Loaded by the visitor's browser from Google Fonts (we do not host or modify the font files). "
        "Both are licensed under the SIL Open Font License 1.1, which allows free use, including commercial use.", "",
        "| Font | Designer | Licence | Source |", "|---|---|---|---|",
        *[f"| {n} | {d} | {lic} | {url} |" for n, d, lic, url in FONTS], "",
        "## Images and icons", "",
        "The application ships **no image files**. Emoji are standard Unicode characters drawn by the visitor's own device. "
        "Status badges in the README come from shields.io.", "",
        "## Frontend (Streamlit app)", "",
        "| Package | Licence | Website |", "|---|---|---|",
        *[f"| {n} | {lic} | {url} |" for n, lic, url in FRONTEND], "",
        f"## Backend (API server): {len(rows)} packages, including indirect dependencies", "",
        "| Package | Version | Licence | Website |", "|---|---|---|---|",
        *[f"| {r['Name']} | {r['Version']} | {r['License'].replace('|', '/')} | {r['URL']} |" for r in rows], "",
        "## Notes", "",
        "- **psycopg2-binary** is LGPL-licensed. It is used unmodified as a library, which the LGPL permits.",
        "- **certifi** is MPL-2.0 and is used unmodified.",
        "- Licence texts are included in each package's own distribution (see its website above).", "",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT} ({len(rows)} backend packages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
