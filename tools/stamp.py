#!/usr/bin/env python3
"""
Stamps the 'last verified' banner onto every page of the probate site.

One source of truth: verified.json in the repo root. The weekly verification
job updates that file ONLY after a check actually ran and passed, then runs
this script. The date must never move on a schedule alone, because a freshness
date nobody earned is worse than no date.

Usage:
    python3 stamp.py                 # stamp every page from verified.json
    python3 stamp.py --check         # report what the date would be, change nothing
"""
import json, re, sys, pathlib, datetime

REPO = pathlib.Path(__file__).resolve().parent.parent
STATE = REPO / "verified.json"

START = "<!--VERIFIED:START-->"
END = "<!--VERIFIED:END-->"

def human(iso):
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%B %-d, %Y")

def banner(state):
    d = human(state["verified_on"])
    what = state.get("scope", "Statutes, offices and phone numbers re-checked against primary sources.")
    return (
        f'{START}\n'
        f'  <div class="verified">\n'
        f'    <span class="vlabel">Last verified</span>\n'
        f'    <span class="vdate">{d}</span>\n'
        f'    <span class="vwhat">{what} '
        f'<a href="/how-this-is-checked/">How this is checked</a></span>\n'
        f'  </div>\n'
        f'  {END}'
    )

def stamp(path, block):
    html = path.read_text(encoding="utf-8")
    if START in html and END in html:
        new = re.sub(
            re.escape(START) + r".*?" + re.escape(END),
            lambda _m: block, html, flags=re.S)
    else:
        # Insert immediately after the closing </header> tag.
        if "</header>" not in html:
            return False, "no </header>"
        new = html.replace("</header>", "</header>\n\n  " + block, 1)
    if new == html:
        return False, "unchanged"
    path.write_text(new, encoding="utf-8")
    return True, "ok"

def main():
    if not STATE.exists():
        print(f"missing {STATE}", file=sys.stderr); return 1
    state = json.loads(STATE.read_text())
    block = banner(state)

    if "--check" in sys.argv:
        print(f"verified_on: {state['verified_on']}  ({human(state['verified_on'])})")
        print(f"scope: {state.get('scope','')}")
        return 0

    pages = sorted(REPO.glob("*.html")) + sorted(REPO.glob("*/index.html"))
    pages = [p for p in pages if p.name != "google215180be82bd40a5.html"]
    done = 0
    for p in pages:
        ok, why = stamp(p, block)
        if ok:
            done += 1
        elif why != "unchanged":
            print(f"  skip {p.relative_to(REPO)}: {why}")
    print(f"stamped {done} of {len(pages)} pages with {human(state['verified_on'])}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
