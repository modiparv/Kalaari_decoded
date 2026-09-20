# Kalaari Decoded

An interactive intelligence tool built from everything public about [Kalaari Capital](https://kalaari.com):
what the firm does, what it says it wants, every portfolio company we could trace (with founders and
founder-age signals), the team, and a **deal-fit scanner** the Kalaari team can use to triage inbound decks.

Open `index.html` in any browser. It is one self-contained file: no server, no build step needed to view it.

## What is inside

| Section | What it answers |
|---|---|
| At a glance | AUM, companies, unicorns, IPOs, four funds, the 2006 → 2026 timeline, programs (CXXO, Kstart, Fellowship, Alpha Archives) |
| What they want | Stage, first-cheque range, geography, founder filter ("potential over pedigree", founder-market fit, speed to value), how to pitch, Fund IV focus areas with the deals that back each, the firm's own research reports |
| Portfolio explorer | 91 traced companies, filterable by sector, entry stage, status, program and fund era; cards or table; founders, founder age (reported vs estimated), latest round and sources |
| Portfolio decoded | Sector mix, entry year by sector, stage at first cheque, outcomes, founder-age bands, Fund IV founder profile. Every chart has a hover layer and a table view |
| Thesis vs deployment | Fund IV's stated focus areas against companies actually backed since 2020, with thin areas flagged |
| Deal-fit scanner | Score a deal 0–100 against Kalaari's stated filter, see the nearest portfolio companies (conflicts or intros), get the team member it should route to, keep a per-browser shortlist |
| Team | Investment team, venture partners and operations, from kalaari.com/teams |

## Files

```
index.html                 built dashboard (do not edit by hand)
src/index.template.html    page source; data is inlined at the /*__DATA__*/ marker
data/kalaari.json          the dataset: firm, thesis, funds, programs, team, companies
scripts/build.py           inlines data/kalaari.json into src/ → index.html, with validation
scripts/scrape_kalaari.py  pulls fresh portfolio/team/why-we-invested pages from kalaari.com
```

## Refreshing the data

```bash
python scripts/scrape_kalaari.py        # writes data/kalaari_site_raw.json (needs network access to kalaari.com)
# review the raw pull, merge changes into data/kalaari.json by hand
python scripts/build.py                 # regenerates index.html
```

The scraper tries the WordPress REST API (`/wp-json/wp/v2/portfolio`, `/kalaari_team`, `/posts`) and falls back to
the sitemap plus HTML parsing. It was written in an environment that could not reach kalaari.com, so run it once
with `--limit 5` first and adjust the field regexes in `parse_page()` if the page markup differs.

## Data provenance and caveats

- Compiled September 2026 from kalaari.com page metadata surfaced through web search plus press coverage
  (YourStory, Inc42, Entrackr, Forbes India, Business Standard, Tracxn and Crunchbase summaries). The site itself
  was not directly fetchable during the build, so every company carries a `sources` list and should be treated as a
  lead, not a filing.
- Kalaari states 160+ companies backed; this dataset traces 91 with enough detail to display. Missing ones are
  mostly older Fund I–II positions without a live portfolio page.
- **Founder ages.** `confidence: "reported"` means a dated public source states an age (Forbes 30 Under 30, an
  interview). `confidence: "estimated"` is derived from a graduation year or stated career length. No entry is a
  verified date of birth. 31 of 91 companies have any age signal.
- The 8-unicorn count is Kalaari's own; the dataset names seven (Dream11, Cult.fit, Snapdeal, Upstox, ElasticRun,
  Jumbotail, Good Glamm Group).
- Sector buckets are ours (eight, so charts stay colour-safe); Kalaari's own tags are kept in each company's `tags`.

## Adding a company

Append to `data/kalaari.json → companies` with a unique `id`, a `sector` from the `sectors` list, `stage` at
Kalaari's entry, `year` of entry, `status` (Active, Acquired, Exited, IPO, Shut down), `program` (CXXO, Kstart or
empty), `founders`, an optional `founderAge` (`{"value": 29, "basis": "...", "confidence": "reported"}` or
`{"band": "30s", ...}`), and `sources`. `scripts/build.py` refuses duplicate ids and unknown sectors.
