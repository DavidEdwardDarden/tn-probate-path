#!/usr/bin/env python3
"""
Exports the county routing table as open data: CSV and JSON.

The COUNTIES dict in build_directory.py is the source of truth. This publishes it
in formats other people can actually use, because a table buried in a web page is
not a dataset and nobody links to one.

Run after build_directory.py. Writes to data/ at the repo root.
"""
import csv, json, os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_directory as bd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "data")
TODAY = datetime.date.today().isoformat()

OFFICE_CODE = {
    "Clerk and Master": "clerk_and_master",
    "County Clerk": "county_clerk",
    "Circuit Court Clerk": "circuit_court_clerk",
    "Probate Court Clerk": "probate_court_clerk",
    "Call to confirm": "unsettled",
}

def rows():
    for county, v in sorted(bd.COUNTIES.items()):
        office, who, phone, note, slug = v
        yield {
            "county": county,
            "office": office,
            "office_code": OFFICE_CODE.get(office, "unknown"),
            "officeholder": who or "",
            "phone": phone or "",
            "notes": note or "",
            "detail_page": f"https://estate.handofdavid.com/{slug}/" if slug else "",
            "settled": "false" if office == bd.ASK else "true",
            "last_verified": TODAY,
        }

def main():
    os.makedirs(OUT, exist_ok=True)
    data = list(rows())

    fields = ["county","office","office_code","officeholder","phone",
              "notes","detail_page","settled","last_verified"]
    with open(os.path.join(OUT, "tn-probate-filing-offices.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(data)

    payload = {
        "title": "Where Tennessee probate is filed, by county",
        "description": ("The office that receives probate filings in each of Tennessee's 95 "
                        "counties, with the officeholder and the number that reaches them. "
                        "Compiled from each county's own published pages and from the private "
                        "acts and general statutes that decide which office has the duty."),
        "license": "CC BY 4.0",
        "attribution": "estate.handofdavid.com",
        "source": "https://estate.handofdavid.com/data/",
        "methodology": "https://estate.handofdavid.com/how-this-is-checked/",
        "last_verified": TODAY,
        "county_count": len(data),
        "caveats": [
            "Two counties are unsettled in state law and are marked settled=false. In those, a "
            "county private act and the general statute point at different offices, or a court "
            "is mid-transition, and no public record resolves it.",
            "Phone numbers proved the most durable field and addresses the least. Addresses are "
            "given only in notes, and only where a county's own site publishes them.",
            "Where a compiled private act and a county's own current website disagree, this "
            "follows the website, because it describes what happens at the counter.",
        ],
        "counties": data,
    }
    with open(os.path.join(OUT, "tn-probate-filing-offices.json"), "w") as f:
        json.dump(payload, f, indent=2)

    from collections import Counter
    c = Counter(r["office"] for r in data)
    print(f"{len(data)} counties exported to data/")
    for k, n in c.most_common():
        print(f"  {n:>2}  {k}")

if __name__ == "__main__":
    main()
