#!/usr/bin/env python3
"""Generate the statewide probate office directory.

Routing comes from T.C.A. 16-16-201 (chancery holds probate unless otherwise
provided), T.C.A. 18-6-106 (which clerk may serve a probate court, with its
population-bracket exemptions), and a crawl of all 95 counties' currently
effective private acts in the CTAS compilation.

Phone numbers come from the CTAS clerks-of-court file, except where a county's
own site was read directly. Addresses are deliberately left out: state
directories were found to be a building out of date in at least three counties,
and the phone number is the thing that actually helps.
"""
import os, html

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# office codes
CM = "Clerk and Master"
CC = "County Clerk"
CIRC = "Circuit Court Clerk"
PROB = "Probate Court Clerk"
ASK = "Call to confirm"

# county: (office, contact, phone, note, page_slug or None)
COUNTIES = {
 # --- the six that do not use the Clerk and Master at all
 "Davidson": (CIRC, "Joseph P. Day", "615-862-5980",
   "Seventh Circuit Court, Probate Division. The Clerk and Master here does not take probate.", "davidson-county"),
 "Shelby": (PROB, "Eddie S. Jones, Jr.", "901-222-3750",
   "A standing Probate Court with its own elected clerk. Room 124, not the Clerk and Master in Room 308.", "shelby-county"),
 "Rutherford": (CC, "Lisa Duke Crowell", "615-898-7800",
   "General Sessions judges sit as Probate Judge, so filings go to the County Clerk rather than the Clerk and Master. This office runs four locations; probate is a Murfreesboro matter, at 319 N Maple Street. Careful with the county's own filing-fees page: that is the 2016 Chancery schedule and it does not govern probate here, which uses the County Clerk's schedule revised July 1 2018. 615-898-7800 is the number the county publishes. A direct probate line may exist but the county does not publish one, so ask for estates when you call.", "rutherford-county"),
 "Sevier": (CC, "Adra Rowland, County Clerk", "865-453-5502 opt. 5",
   "Probate is handled in-house by the County Clerk; ask for option 5. IMPORTANT: this county's published probate instructions state that filings must be prepared by a Tennessee-licensed attorney. No Tennessee statute requires counsel, so whether that is a local rule or a strong preference is the first thing to ask on the phone. Fees from 01/01/2026: $433.50 for a small estate, muniment, or probate without publication; $503.50 with publication.", None),
 "Putnam": (CIRC, "Jennifer Wilkerson", "931-528-1508",
   "Probate Court under a General Sessions judge; the Circuit Court Clerk is the clerk.", None),
 "Cannon": (CC, "Lana S. Jones, County Clerk", "615-563-4278",
   "County Clerk, under a population exemption at T.C.A. 18-6-106. The office's own page does not list probate, so confirm by phone. Closed Wednesday and Sunday; open Saturday morning.", None),

 # --- non-chancery probate court, but the Clerk and Master still takes the filing
 "Wilson": (CM, "Millie Sloan", "615-466-5311",
   "General Sessions Division III. Probate is Room 201 on its own line, separate from Chancery.", "wilson-county"),
 "Cumberland": (CM, "Benjamin Tollett", "931-484-4731", "Probate and Family Court; Clerk and Master is the clerk.", None),
 "Dyer": (CM, "Cindy Rose", "731-286-7818", "Probate Court under General Sessions; Clerk and Master is the clerk.", None),
 "Monroe": (CM, "Teresa Choate", "423-442-2644", "Probate Court under a General Sessions judge; Clerk and Master since 1990.", None),
 "Roane": (CM, "Pam May", "865-376-2487", "General Sessions; the Clerk and Master clerks probate specifically.", None),
 "White": (CM, "Gena Brock", "931-836-3787", "General Sessions; Clerk and Master performs the probate clerk duties.", None),
 "Henry": (CM, "Albert Wade", "731-642-4234", "General Sessions; Clerk and Master since 2010.", None),
 "Hamilton": (CM, "Rachael J. Kapperman", "423-209-6600",
   "Chancery Part 2. Probate hearings are by appointment only, Tuesday to Friday mornings.", "hamilton-county"),
 "Knox": (CM, "Houston S. Havasy", "865-215-2389",
   "Chancery Probate Division, Suite 352, a different counter from Chancery in Suite 125.", "knox-county"),

 # --- general rule, with a county act that confirms it
 "Carter": (CM, "Andrew LaPorte", "423-542-1801", "Clerk and Master also serves as Clerk of the Probate Court. The county publishes 423-542-1801; an older 423-542-1812 appears nowhere on its page.", None),
 "Giles": (CM, "Crystal Gibson Greene", "931-363-2620", None, None),
 "Macon": (CM, "Kristin Reid", "615-666-2000", None, None),
 "Pickett": (CM, "Leana Neal", "931-864-3359", None, None),
 "Marshall": (CM, "Cecilia Spivy", "931-359-2181", "The separate Probate Court ceased to exist in 1997.", None),
 "McMinn": (CM, "Patty Gaines", "423-745-1281", None, None),
 "Lawrence": (CM, "Kristy Gang", "931-766-4182", None, None),
 "Montgomery": (CM, "Heather L. Moore, JD", "931-648-5703",
   "A full administration requires an attorney here. The small estate exemption is the carve-out.", "montgomery-county"),
 "Overton": (CM, "Dorothy Stanton", "931-823-2536",
   "The office's own mailing line reads Probate and Juvenile Clerk. 100 E. Court Square, Suite 100, Livingston.", None),
 "Sullivan": (CM, "Katharine Jennell", "423-323-6483", "Chancery at Blountville specifically, not Kingsport.", None),
 "Washington": (CM, "Sarah Lawson", "423-788-1450", "The Clerk and Master's Jonesborough office.", None),
 "Jackson": (CM, "Sherrie Pippin-Loftis", "931-268-9516", None, None),
 "Moore": (CM, "Tammy Roberts", "931-759-7028", None, None),
 "Franklin": (CM, "Katelyn Isbell", "931-967-2843", "Moved from General Sessions to Chancery effective July 1, 2014.", None),

 # --- general rule by default
 "Anderson": (CM, "Hal Cousins", "865-457-6205", None, None),
 "Bedford": (CM, "Angela Hayes", "931-684-1672",
   "The published fee schedule dates from 2017. Ask for the current cost.", "bedford-county"),
 "Benton": (CM, "Carly Bayless", "731-584-4435", None, None),
 "Bledsoe": (CM, "Tyler DeBord", "423-447-2484", None, None),
 "Bradley": (CM, "Holly Thompson", "423-728-7204", None, None),
 "Campbell": (CM, "Dennis Potter", "423-562-3496", None, None),
 "Carroll": (CM, "Kenneth Todd", "731-986-1920", None, None),
 "Cheatham": (CM, "Rhonda Vaughn", "615-792-4620", None, None),
 "Chester": (CM, "Keith Frye", "731-989-7171", None, None),
 "Claiborne": (CM, "Patricia Simmons", "423-626-3284", None, None),
 "Clay": (CM, "Rene Davis", "931-243-3145", None, None),
 "Cocke": (CM, "Craig Wild", "423-623-3321", None, None),
 "Coffee": (CM, "Sheila Proffitt", "931-723-5132",
   "E-filing through Tybera, but the original will must be physically delivered.", "coffee-county"),
 "Crockett": (CM, "James Stephenson", "731-696-5458", None, None),
 "Decatur": (CM, "Elizabeth Carpenter", "731-852-3422", None, None),
 "DeKalb": (CM, "Nicole Wright", "615-597-4360", None, None),
 "Fentress": (CM, "Linda Smith", "931-879-8615", None, None),
 "Gibson": (CM, "Katelyn Orgain", "731-855-7639", "Two offices. Trenton is the county seat; Humboldt is 731-784-9551.", None),
 "Grainger": (CM, "Vickie Greenlee", "865-828-4436", None, None),
 "Greene": (CM, "Bland Justis", "423-798-1742", None, None),
 "Grundy": (CM, "Megan Rollins", "931-692-3455", None, None),
 "Hamblen": (CM, "Teresa Carey", "423-586-9112", None, None),
 "Hancock": (CM, "Thomas Harrison", "423-733-4524", None, None),
 "Hardeman": (CM, "Kim Paras", "731-658-3142", None, None),
 "Hardin": (CM, "Jennifer Fielder", "731-925-8166", None, None),
 "Hawkins": (CM, "Brent Price", "423-272-8150", None, None),
 "Haywood": (CM, "Felicia Bond", "731-772-0122", None, None),
 "Henderson": (CM, "Leigh Milam", "731-968-2801", None, None),
 "Hickman": (CM, "Loren Roberts", "931-729-2522", None, None),
 "Houston": (CM, "Patsy Brooks", "931-289-3870", None, None),
 "Humphreys": (CM, "Mike Bullion", "931-296-2558",
   "The Probate and Juvenile Court was repealed effective 2022 and probate returned to chancery. Court offices sit in the Rawlings Building, 102 Thompson Street, though mail goes to the Court Square address.", None),
 "Johnson": (CM, "Sherrie Fenner", "423-727-7853", None, None),
 "Lake": (CM, "Amber Mooring", "731-253-8926", None, None),
 "Lewis": (CM, "Kaitlin Bates", "931-796-3734", None, None),
 "Lincoln": (CM, "Rebecca Bartlett Carpenter", "931-433-1482", None, None),
 "Marion": (CM, "Paige Mashburn", "423-942-2601", None, None),
 "Maury": (CM, "Larry Roe Sr.", "931-375-1307",
   "Probate sits in Chancery. Fees from the schedule effective January 1, 2026: $456.50 to open with publication, $379.50 without, and $379.50 or $384.50 for a small estate. Go between 8:00 and 4:00; the 7:30 to 4:30 figure the county also publishes is staff hours. No e-filing, and a new estate cannot be opened by email or fax.", "maury-county"),
 "McNairy": (CM, "Kimberly Boals", "731-645-5446", None, None),
 "Meigs": (CM, "Donna Moore", "423-334-5243", None, None),
 "Morgan": (CM, "Angela Anderson", "423-346-3881", None, None),
 "Obion": (CM, "Emily Hall", "731-507-0999", None, None),
 "Perry": (CM, "Charlene Duplessis", "931-589-2217", None, None),
 "Polk": (CM, "Kimberly Ingram", "423-338-4522", None, None),
 "Robertson": (CM, "Jon Graves", "615-384-5650",
   "Chancery Court, 422 West Court Square, Room 102, Springfield. Open 8:00 to 4:30, Monday to Friday.", "robertson-county"),
 "Sequatchie": (CM, "Sherry Brock", "423-949-3670", None, None),
 "Smith": (CM, "Jessie Goad", "615-735-2092", None, None),
 "Stewart": (CM, "April Turner", "931-232-5665", None, None),
 "Sumner": (CM, "Mark T. Smith", "615-451-6036",
   "No bags or purses clear security. The office moved to the new courthouse on East Main.", "sumner-county"),
 "Tipton": (CM, "Gina Smith", "901-476-0210", None, None),
 "Trousdale": (CM, "Shelly Brawner", "615-374-2996", None, None),
 "Union": (CM, "Sandra Edmondson", "865-992-5942", None, None),
 "Warren": (CM, "Myra Mara", "931-473-2364", None, None),
 "Wayne": (CM, "Jamie Ann White", "931-722-5517", None, None),
 "Weakley": (CM, "Regina VanCleave", "731-364-3454", None, None),
 "Williamson": (CM, "Jakob L. Schwendimann", "615-790-5428",
   "Electronic filing through Tybera is required. Estates line is 615-591-8538.", "williamson-county"),

 # --- documented conflict between a private act and the statute. Call first.
 "Blount": (CM, "Stephen Ogle", "865-273-5500",
   "A General Sessions judge sits in probate, and the Clerk and Master clerks that docket. Fees from 01/01/2026: $345.00 for a small estate, a full administration, or muniment of title; $431.40 with creditor notice. Cash, money order, cashier's check or a law firm check only, no cards.", None),
 "Dickson": (CM, "Lynn Collins", "615-789-7011",
   "The county's Probate and Juvenile Court was never given jurisdiction over decedents' estates, only over juveniles, so estate filings go to the Clerk and Master. Do not call 615-789-5414, which is the General Sessions clerk.", None),
 "Fayette": (CM, "Amy Anderson", "901-465-5219",
   "Chancery Court lists open estates among its services, and the County Clerk lists no probate function at all. Fees are not published; call.", None),
 "Jefferson": (CC, "Frank Herndon, County Clerk", "865-397-2935",
   "The County Clerk runs the probate section here, with its own intake form and fee schedule. Small estate $354.50, opening an estate $523.50, or $354.50 with no creditor notice. Open Saturday 8 to 11. Do not call 865-397-2404, which is the Clerk and Master.", None),
 "Lauderdale": (ASK, "Minnie Stowe", "731-635-1941",
   "This county is mid-transition. Private Acts of 2025 ch. 16 dissolves the Probate and Juvenile Court, but only when the sitting judge's full term expires, and separately permits the county commission to move the probate clerking at any time before that. No published record says whether it has. The 1982 act naming the County Clerk as probate clerk was left unamended and still stands on its face. Call the Clerk and Master at 731-635-1941 and ask whether estate petitions are being received there; if not, the County Clerk is 731-635-2561. Ask which building too, because the 2025 act ordered the court moved to the Justice Complex and three addresses are in circulation.", None),
 "Loudon": (PROB, "Steve Harrelson", "865-986-3505",
   "One officeholder is the Circuit, Criminal, Sessions, Juvenile and Probate Court Clerk. Probate is heard in General Sessions at the Justice Center in Lenoir City, 12680 Highway 11 West, Suite 3. Not the County Clerk and not the Clerk and Master.", None),
 "Madison": (ASK, "Sharon Perry-Brown", "731-423-6030",
   "Sources conflict and the county publishes nothing that settles it. One set of records puts probate in General Sessions Division II at the Juvenile Court Complex on Irby Street, with its own line at 731-988-3025. Call the Clerk and Master at 731-423-6030 and ask which office takes estate filings and in which building.", None),
 "Rhea": (CC, "Linda Shaver, County Clerk", "423-775-7808",
   "A 1982 act vests probate in General Sessions with the County Clerk as its clerk, and expressly divested the Clerk and Master. The county website is offline and two addresses circulate, so confirm the street address when you call.", None),
 "Scott": (ASK, "Michael Potter", "423-663-2627",
   "Private Acts of 1982 ch. 383 vests all probate jurisdiction in General Sessions and names no clerk for it. Private Acts of 1951 ch. 657 makes the Circuit Court Clerk the clerk of General Sessions, which points one way. T.C.A. 18-6-106 points instead at the Clerk and Master. The county publishes nothing either way and the state's own compilation declines to name a current probate clerk, so both offices are legally defensible. Call the Clerk and Master at 423-663-2627 and the Circuit Court Clerk at 423-663-2440 and ask which one takes estate filings.", None),
 "Unicoi": (CM, "Teresa Simerly", "423-743-9541",
   "An Attorney General opinion issued about this county moved probate clerking off the County Clerk, and the Clerk and Master is where it lands. The County Clerk lists no probate function. Mail goes to PO Box 46, not the general county box. Confirm before filing.", None),
 "Van Buren": (CM, "Tina Shockley", "931-946-7175",
   "A 1986 act that would have moved probate to the General Sessions clerk was rejected by local voters and never took effect, so probate stayed in chancery. Confirm the street address when you call.", None),
}

HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Where Tennessee Probate Is Filed</title>
<meta name="description" content="Which office takes probate in each of Tennessee's 95 counties, with the phone number. Six counties do not use the Clerk and Master. Built from the statutes and every county's private acts.">
<link rel="canonical" href="https://estate.handofdavid.com/where-to-file/">
<style>
  :root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
  *{box-sizing:border-box}
  body{margin:0}
  img{max-width:100%}
  [hidden]{display:none!important}
</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,600;1,6..72,400&family=Public+Sans:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/styles.css">
</head>
<body>
'''

BADGE = {
    CM:   ("Clerk and Master", "ok"),
    CC:   ("County Clerk", "alt"),
    CIRC: ("Circuit Court Clerk", "alt"),
    PROB: ("Probate Court Clerk", "alt"),
    ASK:  ("Unsettled in state law", "warn"),
}


def build():
    out = HEAD + '\n<div class="wrap">\n  <header>\n'
    out += '    <div class="crumb"><a href="/">Tennessee probate</a> &#183; All 95 counties</div>\n'
    out += '    <h1>Where Tennessee probate is actually filed</h1>\n'
    out += ('    <p class="standfirst lede">Every county, the office that takes the filing, and the number '
            'that reaches it. Eighty-four counties use the Clerk and Master. Eleven do not, and walking into '
            'the wrong office costs you a morning.</p>\n')
    out += '  </header>\n\n'

    out += '''  <div class="notice">
    <h2>Why this page exists</h2>
    <p>No published list of this exists. Tennessee's default rule sends probate to Chancery Court and the Clerk and Master, but individual counties have private acts that move it, and a 2003 statute barring county clerks from serving probate courts carved out exemptions by population bracket. The result is a patchwork that statewide guides flatten and get wrong. This was built by reading the two controlling statutes and every county's currently effective private acts.</p>
  </div>

  <div class="card">
    <h2 class="sec">The nine exceptions</h2>
    <p>If the estate is in one of these counties, the Clerk and Master is the wrong office.</p>
    <div class="block">
      <ul>
        <li><b>Davidson.</b> Seventh Circuit Court, Probate Division. File with the Circuit Court Clerk. The Clerk and Master here does not take probate.</li>
        <li><b>Shelby.</b> A standing Probate Court with its own separately elected clerk, in Room 124.</li>
        <li><b>Putnam.</b> Probate Court under a General Sessions judge, clerked by the Circuit Court Clerk.</li>
        <li><b>Loudon.</b> One officeholder is the Circuit, Criminal, Sessions, Juvenile and Probate Court Clerk. File there, at the Justice Center in Lenoir City.</li>
        <li><b>Rutherford.</b> General Sessions judges sit as Probate Judge. File with the County Clerk, in Murfreesboro, not at one of its other three offices.</li>
        <li><b>Jefferson.</b> County Clerk, which runs its own probate section with its own intake form and fee schedule.</li>
        <li><b>Rhea.</b> County Clerk. A 1982 act vested probate exclusively in General Sessions and expressly divested the Clerk and Master.</li>
        <li><b>Sevier.</b> County Clerk's probate clerks. Ask for option 5.</li>
        <li><b>Cannon.</b> County Clerk, under a population exemption at T.C.A. 18-6-106.</li>
      </ul>
    </div>
    <p>Two more, <b>Scott</b> and <b>Lauderdale</b>, are unsettled in state law. The reasons are under their entries below.</p>
    <p>Several more counties hear probate somewhere other than Chancery while the Clerk and Master still takes the filing: Wilson, Cumberland, Dyer, Monroe, Roane, White, Henry, Blount and Madison. Right office, unusual court. <b>Knox and Hamilton are not in that group</b>; both keep probate inside Chancery as a named division, which is why their own pages say there is no separate probate court.</p>
  </div>

  <div class="card">
    <h2 class="sec">Take this as a file</h2>
    <p>The whole table is published as <a href="/data/">open data</a>, CSV and JSON, licensed CC BY 4.0. If you maintain a national probate resource and Tennessee is the state you cannot keep current, it is yours.</p>
  </div>

  <div class="card">
    <h2 class="sec">Every county</h2>
    <p>Type to filter. Two counties are marked <b>Unsettled in state law</b>. In those, a county private act and the general statute point at different offices and no public record resolves it, or a court is mid-transition under an act that has not finished taking effect. The reason is stated under each one, and the number listed reaches someone who can answer it today.</p>
    <input type="search" id="filter" placeholder="Start typing a county name" autocomplete="off">
    <div class="feewrap">
      <table class="fees" id="counties">
        <thead><tr><th>County</th><th>File with</th><th>Phone</th></tr></thead>
        <tbody>
'''

    for name in sorted(COUNTIES):
        office, contact, phone, note, slug = COUNTIES[name]
        label, cls = BADGE[office]
        cname = f'<a href="/{slug}/">{html.escape(name)}</a>' if slug else html.escape(name)
        bits = [f'<span class="badge {cls}">{label}</span>']
        if contact:
            bits.append(f'<span class="who">{html.escape(contact)}</span>')
        if note:
            bits.append(f'<span class="cnote">{html.escape(note)}</span>')
        out += (f'          <tr><td data-c="{html.escape(name).lower()}"><b>{cname}</b></td>'
                f'<td>{"".join(bits)}</td>'
                f'<td>{html.escape(phone) if phone else "see note"}</td></tr>\n')

    out += '''        </tbody>
      </table>
    </div>
    <p class="fee-note" id="count"></p>
  </div>

  <div class="card">
    <h2 class="sec">Why there are no addresses here</h2>
    <p>Because the official ones disagree. Checking a single county turned up three different addresses for the same office across three state and county sources, all of them current-looking. Another county's office had moved to a new courthouse while the state directory still listed the old building.</p>
    <p>Phone numbers held up where addresses did not. So this page gives you the number, and the person who answers it will tell you which door, what it costs today, and whether you need an appointment. That is a better answer than a street address that was right last year.</p>
  </div>

  <div class="card">
    <h2 class="sec">Counties written up in full</h2>
    <p>Office, fee schedule, local rules, and what to carry in.</p>
    <div class="county-list">
      <a href="/rutherford-county/">Rutherford</a>
      <a href="/davidson-county/">Davidson</a>
      <a href="/williamson-county/">Williamson</a>
      <a href="/wilson-county/">Wilson</a>
      <a href="/sumner-county/">Sumner</a>
      <a href="/coffee-county/">Coffee</a>
      <a href="/montgomery-county/">Montgomery</a>
      <a href="/knox-county/">Knox</a>
      <a href="/hamilton-county/">Hamilton</a>
      <a href="/shelby-county/">Shelby</a>
      <a href="/maury-county/">Maury</a>
      <a href="/bedford-county/">Bedford</a>
      <a href="/robertson-county/">Robertson</a>
    </div>
  </div>

  <div class="offer">
    <h3>Hand the paperwork part to me</h3>
    <p>Whichever office you end up at, the filing asks for the same two things: everything the person owned, valued at the date of death, and everything they owed, with addresses and amounts. Building those from a shoebox of statements is the part that takes a week of evenings.</p>
    <ul>
      <li>An asset list with date-of-death values, in the order the filing asks for them</li>
      <li>A debt and creditor list with names, addresses, and amounts</li>
      <li>A running estate account you keep adding to as money moves</li>
      <li>Delivered as a spreadsheet and a PDF within two business days</li>
    </ul>
    <p class="price">$249 flat. Nothing owed until you have seen it.</p>
    <p>Send me the county and roughly what the estate holds, and I will tell you exactly what to scan and what to leave alone.</p>
    <div class="contact">
      <span class="addr">david@handofdavid.com</span>
    </div>
  </div>

  <footer>
    <p><b>This is organization, not legal advice.</b> It points you at the right office so you are not standing at the wrong window. Call before you drive.</p>
    <p>Routing from <code>T.C.A. &#167; 16-16-201</code> (chancery holds probate unless otherwise provided), <code>&#167; 18-6-106</code> (which clerk may serve a probate court, and the population brackets exempted from it), and the currently effective private acts of all 95 counties as compiled by the University of Tennessee County Technical Assistance Service. Officeholders and phone numbers from the state clerks-of-court file and from county sites read directly.</p>
    <p>Built and checked on <b>October 27, 2026</b>, by David Darden, Murfreesboro, Tennessee. Counties change their arrangements by private act, and an act passed after this date will not be here. Call before you rely on it.</p>
  </footer>
</div>

<script>
(function(){
  var box = document.getElementById('filter');
  var rows = [].slice.call(document.querySelectorAll('#counties tbody tr'));
  var count = document.getElementById('count');
  function show(n){ count.textContent = n + ' of ' + rows.length + ' counties shown.'; }
  show(rows.length);
  box.addEventListener('input', function(){
    var q = box.value.trim().toLowerCase();
    var n = 0;
    rows.forEach(function(r){
      var hit = !q || r.firstElementChild.getAttribute('data-c').indexOf(q) === 0;
      r.hidden = !hit;
      if (hit) n++;
    });
    show(n);
  });
})();
</script>

</body>
</html>
'''
    d = os.path.join(REPO, "where-to-file")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w") as f:
        f.write(out)
    return len(COUNTIES), len(out)


if __name__ == "__main__":
    n, size = build()
    print(f"{n} counties, {size} bytes")
