# Kalaari Decoded

Paste a startup's website and see whether [Kalaari Capital](https://kalaari.com) would back it. The page reads
the site, fills in the deal details, and scores them against exactly two things: **Kalaari's public investment
thesis** (60 points) and **Kalaari's portfolio** of 91 traced companies (40 points). Every point comes with the
evidence behind it, the closest portfolio companies are listed for conflict checks or intros, and a one-click memo
goes to the clipboard.

Live: https://kalaari-decoded-modiparvs-projects.vercel.app

## How the score works

| Thesis · 60 | Portfolio · 40 |
|---|---|
| Stage of round (20): pre-seed to Series A, first institutional cheque | Pattern (15): companies in this sector Kalaari backed since 2020 |
| Cheque (15): $0.5–5M first cheque; avg $2.2M seed, $4.9M Series A | Adjacency (10): keyword overlap with the nearest portfolio company |
| Sector (15): the named Fund IV focus areas | Conflict (10): full points unless an active portfolio company is a direct competitor |
| Geography (10): India-first, India-only LP | Precedent (5): Kalaari has entered this sector at this stage before |

Founder signals (first-time, repeat, woman founder-CEO, AI-native, traction) are shown as tags, not points,
because Kalaari says "potential over pedigree" and backs pre-traction teams.

## Website extraction

`api/extract.js` is a Vercel serverless function. `GET /api/extract?url=<site>` fetches the homepage and one
about/team page server-side and returns structured fields (name, one-liner, sector, HQ, founders, founding year,
AI-native, funding stage and size if mentioned, evidence).

- With `ANTHROPIC_API_KEY` set in the Vercel project, the page text is sent to Claude (`claude-opus-5`) with a
  strict output schema. This is the accurate mode.
- Without it, a keyword/regex heuristic runs. It gets sector, HQ and founders right often enough to triage, but
  check stage and round size by hand (sites rarely state them).
- Only public http(s) hosts are fetched; localhost and private ranges are refused.

Set the key under Vercel → Project → Settings → Environment Variables → `ANTHROPIC_API_KEY`, then redeploy.

## Files

```
public/index.html          built page (do not edit by hand)
src/index.template.html    page source; data is inlined at the /*__DATA__*/ marker
api/extract.js             Vercel function: website → structured deal fields
data/kalaari.json          the dataset: firm, thesis, funds, programs, team, companies
scripts/build.py           inlines data/kalaari.json into src/ → public/index.html, with validation
scripts/scrape_kalaari.py  pulls fresh portfolio/team/why-we-invested pages from kalaari.com
vercel.json                static output from public/, function timeout for api/extract
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
