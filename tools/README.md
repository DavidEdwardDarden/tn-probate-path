# Tools

Two scripts and one rule.

## The rule

**The verified date only moves when a check actually ran and passed.**

A freshness date that advances on a schedule is worse than no date at all. It claims
something nobody earned. That is precisely the failure mode of the stale county pages
this site exists to correct, and copying it would make this site one of them.

If a weekly check cannot be completed, leave the date where it is and say so.

## build_directory.py

Generates `where-to-file/index.html` from the `COUNTIES` dict at the top of the file.
That dict is the source of truth for county routing. Each entry is:

```python
"County": (office, officeholder, phone, note, page_slug_or_None)
```

where `office` is one of `CM` (Clerk and Master), `CC` (County Clerk), `CIRC`
(Circuit Court Clerk), `PROB` (Probate Court Clerk), or `ASK` (call to confirm).

Run it after any change to the dict.

```
python3 tools/build_directory.py
```

## stamp.py

Writes the "Last verified" banner into every page, driven by `verified.json` in the
repo root. The banner sits between `<!--VERIFIED:START-->` and `<!--VERIFIED:END-->`
markers, or is inserted after `</header>` if the markers are absent.

```
python3 tools/stamp.py           # stamp all pages
python3 tools/stamp.py --check   # print the current date, change nothing
```

## Order matters

`build_directory.py` overwrites `where-to-file/index.html` and loses its banner.
**Always run `stamp.py` after `build_directory.py`.**

```
python3 tools/build_directory.py && python3 tools/stamp.py
```

## verified.json

```json
{
  "verified_on": "YYYY-MM-DD",
  "scope": "one sentence shown on the page about what was checked",
  "history": [ { "date": ..., "checked": ..., "unresolved": [...] } ]
}
```

Append to `history` on every check, including checks that found nothing wrong.
The history is the evidence that the date means something.

## Counties still unresolved

Two, as of October 27 2026. Both need a phone call, not more desk research.

| County | Call | Ask |
|---|---|---|
| Scott | 423-663-2440 and 423-663-2627 | Which office takes estate filings |
| Lauderdale | 731-635-1941, then 731-635-2561 | Whether the Clerk and Master is receiving estate petitions yet, and which building |

Five more would benefit from a confirming call: Rhea (street address), Van Buren
(confirm and street address), Unicoi (confirm), Cannon (confirm), Humphreys (confirm
the Rawlings Building rather than Court Square).

## Sources that have proven unreliable

- **CTAS directories.** Actively wrong on Humphreys (lists a court repealed in 2022),
  Rhea's General Sessions judge, and Madison's Juvenile Court Clerk's first name.
- **tncourts.gov clerk directory.** Behind a browser-validation wall; unreadable.
- **swiftprobate.com, weareatticus.com**, and scraped mirrors of them. Generated per
  county, cite nothing, and still describe the pre-2023 "small estate affidavit" on
  pages stamped as updated in 2026.
- **Addresses generally.** The least reliable field in every official source. Phone
  numbers held up best.
- **fayettecountytn.gov** is a parked page, not Fayette County. **rheacountytn.com** is
  offline. **lctngov.com** (Lauderdale) is stale to 2019.

When a compiled private act and a county's own current website disagree, the website
describes what actually happens at the counter. Go with the website, and say in the
note that the act reads otherwise.
