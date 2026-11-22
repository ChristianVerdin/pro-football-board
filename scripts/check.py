#!/usr/bin/env python3
"""Repo hygiene: stats-only wording, no private names, privacy manifests present. Stdlib only."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_SUFFIXES = (".md", ".swift", ".yml", ".yaml", ".json", ".strings", ".txt", ".plist", ".xcprivacy", ".py", ".sh")
SELF = "scripts/check.py"
# The support address is already public on the board's support page.
PUBLIC_CONTACT = "hoynelabs" + "@" + "gm" + "ail.com"

# Built from fragments so this file never matches itself.
BETTING = re.compile(r"\b(" + "|".join((
    "od" + "ds", "spr" + "eads?", "money" + "lines?", "over" + "/under", "par" + "lays?", "bet" + "ting", "wag" + "ers?",
    "sports" + "books?", "draft" + "kings", "fan" + "duel", "bet" + "mgm", "pick" + "center", "against" + "the" + "spread",
    "over" + "under", "impl" + "ied", "v" + "ig", "handi" + "cap",
)) + r")\b", re.I)
PRIVATE = [re.compile(p, re.I) for p in (
    "nfl" + "_2026", "fan" + "duel_scr", "daily" + "locks", "sports" + "kit", "drunk" + "ryan",
    "/Us" + "ers/", "gm" + r"ail\.com", "bet" + "_slips", "page" + "_grabber", r"\b" + "c" + r"v\b",
)]

failures = []


def tracked() -> list[str]:
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if (ROOT / p).is_file()]


def fail(msg: str) -> None:
    failures.append(msg)


def main() -> int:
    files = tracked()
    for rel in files:
        if rel == SELF or not rel.endswith(TEXT_SUFFIXES):
            continue
        text = (ROOT / rel).read_text(errors="replace")
        m = BETTING.search(text)
        if m:
            fail(f"wagering word in {rel}: {m.group(0)!r}")
        clean = text.replace(PUBLIC_CONTACT, "")
        for pat in PRIVATE:
            m = pat.search(clean)
            if m:
                fail(f"private name in {rel}: {m.group(0)!r}")
    for target in ("ProFootballBoard", "ProFootballBoardWidget"):
        f = ROOT / target / "PrivacyInfo.xcprivacy"
        if not f.is_file():
            fail(f"{target}/PrivacyInfo.xcprivacy missing")
        elif "NSPrivacyAccessedAPICategoryUserDefaults" not in f.read_text() or "CA92.1" not in f.read_text():
            fail(f"{target} privacy manifest does not declare UserDefaults CA92.1")
    for line in failures:
        print("FAIL", line)
    print(f"{len(files)} files checked, {len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
