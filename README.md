# Kalaari Decoded

A deal-fit scanner and fund-plan workbench for the [Kalaari Capital](https://kalaari.com) investment team.
Paste a startup's website; the app reads the site, fills in the deal, and scores it against three things the team
controls: **the thesis**, **the portfolio** and **the fund plan**. Nothing else feeds the score.

Live: https://kalaari-decoded-modiparvs-projects.vercel.app

## The five tabs

| Tab | What it is for |
|---|---|
| **Scan** | One website in, one score out. Details are read from the site (editable), the score is split into thesis, portfolio and plan points with a line of evidence per check, the closest portfolio companies are listed with a conflict flag, and the deal can go to the pipeline or be copied as a memo. "Scan a list" does the same for a pasted list of websites. |
| **Pipeline** | Every deal you kept, with status (New → Screening → Partner meeting → IC → Invested / Passed), owner and notes. Open any row to re-score it; export as CSV. |
| **Fund plan** | Fund size, window, target company count, reserves, typical cheque by stage, sector and stage targets. The dashboard shows companies and estimated capital deployed against plan, sector and stage mix versus target, pacing per year, and CXXO deployment. |
| **Portfolio** | The companies the scanner compares against. Edit anything, add companies, enter actual cheques, import a CSV, export CSV or JSON. Edits are stored as overrides on top of the base data. |
| **Settings** | Weights for every check, thesis rules (focus sectors, stage points, cheque band, geography, verdict thresholds), the sector list, routing by sector, extractor status, and workspace export / import / share link. |

## How the score is built

Each check earns a fraction of its weight; the score is points earned ÷ points available, shown out of 100.
Any weight can be set to 0 to switch a check off. Defaults:

| Group | Check | Default weight | Rule |
|---|---|---|---|
| Thesis | Stage | 18 | Stage points table (pre-seed and seed 100%, Series A 85%, Series B 30%, later 0%) |
| Thesis | Cheque | 14 | Full inside the first-cheque band ($0.5–5M), partial when unknown or just above, low when far above |
| Thesis | Sector | 14 | Full for focus sectors, a set percentage otherwise |
| Thesis | Geography | 9 | India 100%, global-from-India 80%, outside India 20% |
| Portfolio | Pattern | 13 | Number of companies in this sector backed inside the fund window |
| Portfolio | Adjacency | 9 | Weighted keyword overlap with the nearest portfolio company (rare words count more) |
| Portfolio | Conflict | 9 | Full unless an active portfolio company in the same sector shares two or more distinctive terms |
| Portfolio | Precedent | 4 | Whether the fund has entered this sector at this stage before |
| Plan | Allocation | 6 | Where the sector would sit against its target after this deal (under target earns full points) |
| Plan | Capacity | 4 | Slots and estimated initial capital left in the fund |

Founder signals (first-time, repeat, operator, woman founder-CEO, AI-native, traction) appear as tags, not points,
because Kalaari says "potential over pedigree" and backs pre-traction teams. Change that in Settings if you disagree.

## Using it inside portfolio planning

1. **Set the plan once** (Fund plan tab). Pre-filled from public sources: Fund IV, $200M committed by Reliance via
   Jio Platforms (2021), CXXO $10M a year. Target count, reserves and sector/stage targets ship blank; nothing is
   invented. Share the settings link so everyone scores against the same plan.
2. **Keep the portfolio honest** (Portfolio tab): enter actual cheques for fund-window companies so "capital
   deployed" stops being an estimate; add companies the base data missed; fix sectors.
3. **Triage inbound with Scan**: the Plan fit group tells you whether a deal fills a gap or deepens an overweight;
   the Conflict check tells you whether to ask a portfolio founder first.
4. **Run the pipeline** from the Pipeline tab; export CSV for the Monday meeting.
5. **Review the dashboard monthly**: sector and stage drift, pacing against target, CXXO deployment against its
   annual budget.

## Where things are stored

Settings, portfolio edits and the pipeline live in the browser's local storage. To move them between people or
machines use **Export workspace / Import workspace** (everything) or **Copy share link** (settings only). To make a
portfolio correction permanent for everyone, edit `data/kalaari.json` and rebuild.

## Website reading

`api/extract.js` is a Vercel serverless function. `GET /api/extract?url=<site>` fetches the homepage plus one
about/team page and returns structured fields. `GET /api/extract?probe=1` reports which mode is active.

- With `ANTHROPIC_API_KEY` set on the Vercel project, page text goes to Claude (`claude-opus-5`) under a strict
  output schema. Founders and funding are filled only when the site states them.
- Without it, a keyword heuristic runs. It gets sector, HQ, founders and any stated funding; stage and round size
  are usually unknown, and the Scan tab says so.
- JavaScript-only sites yield little text; the app flags them and asks for the fields by hand.
- Only public http(s) hosts are fetched; localhost and private ranges are refused.

Set the key under Vercel → Project → Settings → Environment Variables → `ANTHROPIC_API_KEY`, then redeploy.

## Files

```
public/index.html          built app (do not edit by hand)
src/index.template.html    app source; data is inlined at the /*__DATA__*/ marker
api/extract.js             Vercel function: website → structured deal fields
data/kalaari.json          base dataset: firm, thesis, funds, programs, team, companies
scripts/build.py           inlines data/kalaari.json into src/ → public/index.html, with validation
scripts/scrape_kalaari.py  pulls fresh portfolio/team/why-we-invested pages from kalaari.com
vercel.json                static output from public/, function timeout for api/extract
```

## Data provenance and caveats

- Base data compiled September 2026 from kalaari.com page metadata surfaced through search plus press coverage.
  91 of Kalaari's 160+ companies are traced; missing ones are mostly older Fund I–II positions.
- Per-company cheques are not public. The dashboard estimates them from the per-stage cheque in Fund plan and
  marks them "est." until you enter actuals. Seed ($2.2M) and Series A ($4.9M) averages come from a third-party
  investor profile; pre-seed and Series B figures are placeholders.
- Fund sizes in `data/kalaari.json` carry a `confidence` field. Fund II (~$150M, 2012) and Fund IV ($200M
  Reliance commitment, 2021) are reported by sources read during research; Fund I and Fund III sizes are marked
  unverified and left null.
- Founder ages in the data file are `reported` only where a dated public source states one; otherwise `estimated`.
- The extractor and scoring are triage aids. They do not replace diligence.

## Developer notes

`window.KD` exposes `cfg`, `score`, `read`, `fill`, `portfolio`, `planStats`, `addToPipeline`, `importPortfolioCSV`,
`exportWorkspace`, `importWorkspace`, `shareLink` and `showTab` for debugging and tests. The Playwright test used
during development lives outside the repo; a copy is easy to recreate from those hooks.
