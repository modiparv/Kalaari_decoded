#!/usr/bin/env python3
"""Rebuild the MIS case-study numbers from the source workbook.

Usage:
    python3 analysis.py <path to MIS_FellowshipVCaseStudy_.xlsx> [out_dir]

Reads the four sheets (Summary MIS, KPIs, P&L as per FS, Balance Sheet as per FS),
recomputes every derived metric used in MIS_Analysis.md from the raw inputs (never
from the sheet's own formula cells, several of which are wrong), writes
`derived_metrics.md` and the SVG charts under `charts/`.

Only the standard library plus openpyxl are needed; no plotting library.
"""
import csv
import math
import os
import sys

import openpyxl

# --------------------------------------------------------------------------- load

SRC = sys.argv[1] if len(sys.argv) > 1 else "MIS_FellowshipVCaseStudy_.xlsx"
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
CHARTS = os.path.join(OUT, "charts")
os.makedirs(CHARTS, exist_ok=True)

wb = openpyxl.load_workbook(SRC, data_only=True)
s = wb["Summary MIS"]
k = wb["KPIs"]
pl = wb["P&L as per FS"]
bs = wb["Balance Sheet as per FS"]

QTRS = [s.cell(row=2, column=c).value for c in range(3, 23)]          # Y1 Q1 .. Y5 Q4
YEARS = ["Y1", "Y2", "Y3", "Y4", "Y5"]


def srow(r):
    """Summary MIS row r as a list of 20 quarterly values."""
    return [float(s.cell(row=r, column=c).value or 0) for c in range(3, 23)]


khdr = {c: k.cell(row=3, column=c).value for c in range(3, k.max_column + 1)}
KQ = [c for c, h in khdr.items() if " Q" in str(h)]
KM = [c for c, h in khdr.items() if " M" in str(h)]


def krow(r, cols=KQ):
    out = []
    for c in cols:
        v = k.cell(row=r, column=c).value
        out.append(float(v) if isinstance(v, (int, float)) else 0.0)
    return out


# Summary MIS inputs (hard-coded rows only; formula rows are recomputed)
rev = srow(3)
bl1 = srow(4)
bl2 = [a - b for a, b in zip(rev, bl1)]
cogs = srow(6)
pe = srow(7)
odc = srow(8)
people = srow(11)
sm_np = srow(12)       # S&M, non-people (Summary MIS basis)
ga = srow(13)
rent = srow(14)
others = srow(15)
opex = [sum(x) for x in zip(people, sm_np, ga, rent, others)]
gm = [r - c for r, c in zip(rev, cogs)]
ebitda = [g - o for g, o in zip(gm, opex)]
ebitda_reported = srow(16)   # as shown in the sheet (contains the Y4 Q4 error)
gm_pct_reported = srow(19)

# KPI inputs
open_arr = krow(6)
new_arr = krow(7)
exp_arr = krow(8)
down_arr = krow(9)
churn_arr = krow(10)
close_arr = [o + n + e + d + c for o, n, e, d, c in zip(open_arr, new_arr, exp_arr, down_arr, churn_arr)]
new_cust = krow(13)
open_cust = krow(38)
churn_cust = krow(41)
close_cust = krow(43)
close_mrr = krow(30)
sm_kpi = krow(58)      # "Total Sales & Mkt cost" (KPI basis, ~2.5x the Summary MIS S&M line)
fte = krow(59)

# monthly series for the lumpiness chart
m_hdr = [khdr[c] for c in KM]
m_new = krow(7, KM)
m_churn = krow(10, KM)
m_down = krow(9, KM)
m_exp = krow(8, KM)
m_newcust = krow(13, KM)
m_mrr = krow(30, KM)

# Financial statements (USD '000)
fs = {
    "rev": (pl["C7"].value, pl["D7"].value),
    "other_income": (pl["C8"].value, pl["D8"].value),
    "emp": (pl["C12"].value, pl["D12"].value),
    "other_exp": (pl["C13"].value, pl["D13"].value),
    "da": (pl["C14"].value, pl["D14"].value),
    "loss": (pl["C20"].value, pl["D20"].value),
    "cash": (bs["C29"].value, bs["D29"].value),
    "deferred": (bs["C17"].value, bs["D17"].value),
    "receivables": (bs["C28"].value, bs["D28"].value),
    "payables": (bs["C15"].value + bs["C16"].value, bs["D15"].value + bs["D16"].value),
    "share_cap": (bs["C8"].value, bs["D8"].value),
    "reserves": (bs["C9"].value, bs["D9"].value),
    "equity": (bs["C10"].value, bs["D10"].value),
    "lt_prov": (bs["C12"].value, bs["D12"].value),
    "st_prov": (bs["C18"].value, bs["D18"].value),
    "ppe": (bs["C24"].value, bs["D24"].value),
    "other_nca": (bs["C25"].value, bs["D25"].value),
    "st_loans": (bs["C30"].value, bs["D30"].value),
    "other_ca": (bs["C31"].value, bs["D31"].value),
}

# --------------------------------------------------------------------------- helpers


def yr(vals, y):
    """Sum of the four quarters of year index y (0-based)."""
    return sum(vals[4 * y:4 * y + 4])


def last(vals, y):
    return vals[4 * y + 3]


def first(vals, y):
    return vals[4 * y]


def pct(a, b):
    return a / b if b else float("nan")


def fm(v, unit="k"):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "n/a"
    if unit == "k":
        return f"{v / 1000:,.0f}"
    if unit == "M":
        return f"{v / 1e6:,.2f}"
    if unit == "%":
        return f"{v * 100:,.0f}%"
    if unit == "%1":
        return f"{v * 100:,.1f}%"
    if unit == "x":
        return f"{v:,.1f}x"
    if unit == "n":
        return f"{v:,.0f}"
    return str(v)


# --------------------------------------------------------------------------- annual table

rows = []
A = {}  # annual metrics keyed by name -> list over years
A["Revenue (MIS)"] = [yr(rev, y) for y in range(5)]
A["  Business Line 1"] = [yr(bl1, y) for y in range(5)]
A["  Business Line 2"] = [yr(bl2, y) for y in range(5)]
A["Gross margin"] = [yr(gm, y) for y in range(5)]
A["Gross margin %"] = [pct(yr(gm, y), yr(rev, y)) for y in range(5)]
A["People cost"] = [yr(people, y) for y in range(5)]
A["S&M (non-people, Summary MIS)"] = [yr(sm_np, y) for y in range(5)]
A["S&M (KPI sheet basis)"] = [yr(sm_kpi, y) for y in range(5)]
A["G&A"] = [yr(ga, y) for y in range(5)]
A["Rent & utilities"] = [yr(rent, y) for y in range(5)]
A["Others"] = [yr(others, y) for y in range(5)]
A["Total opex (ex COGS)"] = [yr(opex, y) for y in range(5)]
A["EBITDA (corrected)"] = [yr(ebitda, y) for y in range(5)]
A["EBITDA (as shown in sheet)"] = [yr(ebitda_reported, y) for y in range(5)]
A["EBITDA margin"] = [pct(yr(ebitda, y), yr(rev, y)) for y in range(5)]
A["Closing contracted ARR"] = [last(close_arr, y) for y in range(5)]
A["Closing subscription ARR (MRR x 12)"] = [last(close_mrr, y) * 12 for y in range(5)]
A["New ARR"] = [yr(new_arr, y) for y in range(5)]
A["Expansion ARR"] = [yr(exp_arr, y) for y in range(5)]
A["Downgrade ARR"] = [yr(down_arr, y) for y in range(5)]
A["Churned ARR"] = [yr(churn_arr, y) for y in range(5)]
A["Net new ARR"] = [last(close_arr, y) - first(open_arr, y) for y in range(5)]
A["Gross revenue retention (ARR)"] = [
    pct(first(open_arr, y) + yr(down_arr, y) + yr(churn_arr, y), first(open_arr, y)) for y in range(5)]
A["Net revenue retention (ARR)"] = [
    pct(first(open_arr, y) + yr(exp_arr, y) + yr(down_arr, y) + yr(churn_arr, y), first(open_arr, y)) for y in range(5)]
A["New logos"] = [yr(new_cust, y) for y in range(5)]
A["Churned logos"] = [-yr(churn_cust, y) for y in range(5)]
A["Closing customers"] = [last(close_cust, y) for y in range(5)]
A["Logo churn (annual, on opening)"] = [pct(-yr(churn_cust, y), first(open_cust, y)) for y in range(5)]
A["Avg new ACV"] = [pct(yr(new_arr, y), yr(new_cust, y)) for y in range(5)]
A["Avg ARR per customer (closing)"] = [pct(last(close_arr, y), last(close_cust, y)) for y in range(5)]
A["CAC (KPI S&M / new logos)"] = [pct(yr(sm_kpi, y), yr(new_cust, y)) for y in range(5)]
A["CAC (Summary S&M / new logos)"] = [pct(yr(sm_np, y), yr(new_cust, y)) for y in range(5)]
A["CAC payback, months (KPI S&M, GM-adjusted)"] = [
    12 * pct(yr(sm_kpi, y), yr(new_arr, y) * A["Gross margin %"][y]) for y in range(5)]
A["Magic number, gross (new ARR / KPI S&M)"] = [pct(yr(new_arr, y), yr(sm_kpi, y)) for y in range(5)]
A["Magic number, net (net new ARR / KPI S&M)"] = [pct(A["Net new ARR"][y], yr(sm_kpi, y)) for y in range(5)]
A["Burn multiple (EBITDA burn / net new ARR)"] = [pct(-yr(ebitda, y), A["Net new ARR"][y]) for y in range(5)]
A["Closing FTE"] = [last(fte, y) for y in range(5)]
A["ARR per FTE (closing)"] = [pct(last(close_arr, y), last(fte, y)) for y in range(5)]
A["People cost per avg FTE"] = [pct(yr(people, y), sum(fte[4 * y:4 * y + 4]) / 4) for y in range(5)]

fmt = {
    "Gross margin %": "%", "EBITDA margin": "%", "Gross revenue retention (ARR)": "%",
    "Net revenue retention (ARR)": "%", "Logo churn (annual, on opening)": "%",
    "New logos": "n", "Churned logos": "n", "Closing customers": "n", "Closing FTE": "n",
    "CAC payback, months (KPI S&M, GM-adjusted)": "n",
    "Magic number, gross (new ARR / KPI S&M)": "x", "Magic number, net (net new ARR / KPI S&M)": "x",
    "Burn multiple (EBITDA burn / net new ARR)": "x",
}

lines = []
lines.append("# Derived metrics (rebuilt from raw inputs)\n")
lines.append("All USD, in thousands unless marked. Rebuilt by `analysis.py` from the hard-coded input rows; "
             "the sheet's own formula rows are not used because several are wrong (see MIS_Analysis.md).\n")
lines.append("## Annual view\n")
lines.append("| Metric | " + " | ".join(YEARS) + " |")
lines.append("|---|" + "---:|" * 5)
for name, vals in A.items():
    u = fmt.get(name, "k")
    lines.append(f"| {name} | " + " | ".join(fm(v, u) for v in vals) + " |")

# YoY growth lines
lines.append("\n## Year-on-year growth\n")
lines.append("| Metric | Y2 | Y3 | Y4 | Y5 |")
lines.append("|---|---:|---:|---:|---:|")
for name in ["Revenue (MIS)", "  Business Line 1", "  Business Line 2", "Closing contracted ARR",
             "Closing subscription ARR (MRR x 12)", "New ARR", "Total opex (ex COGS)", "People cost", "Closing FTE"]:
    v = A[name]
    lines.append(f"| {name} | " + " | ".join(fm(pct(v[y] - v[y - 1], v[y - 1]), "%") for y in range(1, 5)) + " |")

# Quarterly table
lines.append("\n## Quarterly view (Y3 Q1 to Y5 Q4)\n")
qi = list(range(8, 20))
lines.append("| Metric | " + " | ".join(QTRS[i] for i in qi) + " |")
lines.append("|---|" + "---:|" * len(qi))
Q = {
    "Revenue": rev, "  BL1": bl1, "  BL2": bl2, "Gross margin % (corrected)": [pct(g, r) for g, r in zip(gm, rev)],
    "Gross margin % (as shown)": gm_pct_reported,
    "Opex ex COGS": opex, "  People": people, "  S&M (Summary)": sm_np, "  G&A": ga, "  Rent": rent, "  Others": others,
    "EBITDA (corrected)": ebitda, "EBITDA (as shown)": ebitda_reported,
    "Opening ARR": open_arr, "New ARR": new_arr, "Expansion": exp_arr, "Downgrade": down_arr, "Churn": churn_arr,
    "Closing ARR": close_arr, "QoQ ARR growth": [pct(c - o, o) for c, o in zip(close_arr, open_arr)],
    "Gross ARR churn % of opening (qtr)": [pct(-(d + c), o) for d, c, o in zip(down_arr, churn_arr, open_arr)],
    "Net ARR retention (qtr)": [pct(o + e + d + c, o) for o, e, d, c in zip(open_arr, exp_arr, down_arr, churn_arr)],
    "New logos": new_cust, "Churned logos": [-x for x in churn_cust], "Closing customers": close_cust,
    "Logo churn % of opening (qtr)": [pct(-c, o) for c, o in zip(churn_cust, open_cust)],
    "S&M (KPI basis)": sm_kpi, "CAC (KPI S&M / new logos)": [pct(a, b) for a, b in zip(sm_kpi, new_cust)],
    "FTE": fte, "ARR per FTE": [pct(a, b) for a, b in zip(close_arr, fte)],
    "Revenue / (sum of monthly MRR in qtr)": [
        pct(rev[i], sum(m_mrr[3 * i:3 * i + 3])) for i in range(20)],
}
qfmt = {"Gross margin % (corrected)": "%", "Gross margin % (as shown)": "%", "QoQ ARR growth": "%",
        "Gross ARR churn % of opening (qtr)": "%", "Net ARR retention (qtr)": "%", "New logos": "n",
        "Churned logos": "n", "Closing customers": "n", "Logo churn % of opening (qtr)": "%", "FTE": "n",
        "Revenue / (sum of monthly MRR in qtr)": "%"}
for name, vals in Q.items():
    u = qfmt.get(name, "k")
    lines.append(f"| {name} | " + " | ".join(fm(vals[i], u) for i in qi) + " |")

# FS reconciliation
lines.append("\n## MIS vs audited financial statements (USD '000)\n")
lines.append("| Line | Y4 FS | Y4 MIS | Diff | Y5 FS | Y5 MIS | Diff |")
lines.append("|---|---:|---:|---:|---:|---:|---:|")
mis_rev = (yr(rev, 3) / 1000, yr(rev, 4) / 1000)
mis_emp = (yr(people, 3) / 1000, yr(people, 4) / 1000)
mis_oth = ((yr(cogs, 3) + yr(sm_np, 3) + yr(ga, 3) + yr(rent, 3) + yr(others, 3)) / 1000,
           (yr(cogs, 4) + yr(sm_np, 4) + yr(ga, 4) + yr(rent, 4) + yr(others, 4)) / 1000)
mis_ebitda = (yr(ebitda, 3) / 1000, yr(ebitda, 4) / 1000)
fs_ebitda = tuple(fs["loss"][i] - fs["other_income"][i] + fs["da"][i] for i in range(2))
for label, f, m in [("Revenue from operations", fs["rev"], mis_rev),
                    ("Employee benefits vs MIS People cost", fs["emp"], mis_emp),
                    ("Other expenses vs MIS COGS+S&M+G&A+Rent+Others", fs["other_exp"], mis_oth),
                    ("EBITDA (FS: loss - other income + D&A) vs MIS", fs_ebitda, mis_ebitda)]:
    lines.append(f"| {label} | {f[0]:,.0f} | {m[0]:,.0f} | {f[0] - m[0]:,.0f} | {f[1]:,.0f} | {m[1]:,.0f} | {f[1] - m[1]:,.0f} |")

# Cash flow derivation
lines.append("\n## Indirect cash flow for Y5, derived from the two balance sheets (USD '000)\n")
d = lambda key: fs[key][1] - fs[key][0]  # noqa: E731
cf = [
    ("Net loss", fs["loss"][1]),
    ("Add back D&A", fs["da"][1]),
    ("Increase in deferred revenue", d("deferred")),
    ("Increase in trade payables", d("payables")),
    ("Increase in provisions", d("lt_prov") + d("st_prov")),
    ("Decrease in trade receivables", -d("receivables")),
    ("Decrease in short-term loans & advances", -d("st_loans")),
    ("Decrease in other current assets", -d("other_ca")),
    ("Increase in other non-current assets", -d("other_nca")),
    ("Capex (change in PPE plus D&A)", -(d("ppe") + fs["da"][1])),
    ("Share capital issued", d("share_cap")),
]
explained = sum(v for _, v in cf)
actual = d("cash")
lines.append("| Item | USD '000 |")
lines.append("|---|---:|")
for label, v in cf:
    lines.append(f"| {label} | {v:,.0f} |")
lines.append(f"| **Explained change in cash** | **{explained:,.0f}** |")
lines.append(f"| **Actual change in cash** | **{actual:,.0f}** |")
lines.append(f"| Unexplained (matches reserves movement not in P&L: {d('reserves') - fs['loss'][1]:,.0f}) | {actual - explained:,.0f} |")

# Runway
y5_burn_cash = -actual
y5_ebitda_burn = -yr(ebitda, 4) / 1000
q4_ebitda_burn_ann = -ebitda[19] * 4 / 1000
cash_end = fs["cash"][1]
lines.append("\n## Runway at end of Y5 (cash USD 11,726k)\n")
lines.append("| Basis | Annual burn (USD '000) | Months of runway |")
lines.append("|---|---:|---:|")
for label, b in [("Y5 actual cash burn (helped by +3,061 deferred revenue and 1,244 other income)", y5_burn_cash),
                 ("Y5 EBITDA burn", y5_ebitda_burn),
                 ("Y5 EBITDA burn less Y5 other income", y5_ebitda_burn - fs["other_income"][1]),
                 ("Y5 Q4 EBITDA burn, annualised", q4_ebitda_burn_ann)]:
    lines.append(f"| {label} | {b:,.0f} | {12 * cash_end / b:,.0f} |")

# Unit economics summary
lines.append("\n## Unit economics (Y5, fully loaded KPI-sheet S&M)\n")
y = 4
acv = A["Avg new ACV"][y]
gmp = A["Gross margin %"][y]
cac = A["CAC (KPI S&M / new logos)"][y]
grr = A["Gross revenue retention (ARR)"][y]
life_arr = 1 / (1 - grr)
life_logo = 1 / A["Logo churn (annual, on opening)"][y]
lines.append("| Item | Value |")
lines.append("|---|---:|")
lines.append(f"| Average new-logo ACV | ${acv / 1000:,.1f}k |")
lines.append(f"| Gross margin | {gmp * 100:.0f}% |")
lines.append(f"| CAC per new logo (KPI S&M basis) | ${cac / 1000:,.1f}k |")
lines.append(f"| CAC per new logo (Summary MIS S&M basis) | ${A['CAC (Summary S&M / new logos)'][y] / 1000:,.1f}k |")
lines.append(f"| CAC payback, gross-margin adjusted | {A['CAC payback, months (KPI S&M, GM-adjusted)'][y]:.0f} months |")
lines.append(f"| Implied customer lifetime from ARR gross retention ({grr * 100:.0f}%) | {life_arr * 12:.0f} months |")
lines.append(f"| Implied customer lifetime from logo churn ({A['Logo churn (annual, on opening)'][y] * 100:.0f}%) | {life_logo * 12:.0f} months |")
lines.append(f"| Sheet's hard-coded lifetime assumption | 36 months |")
for label, life in [("ARR-retention lifetime", life_arr), ("logo-churn lifetime", life_logo), ("36-month assumption", 3.0)]:
    ltv = acv * gmp * life
    lines.append(f"| LTV / CAC using {label} | {ltv / cac:.1f}x (LTV ${ltv / 1000:,.0f}k) |")

with open(os.path.join(OUT, "derived_metrics.md"), "w") as f:
    f.write("\n".join(lines) + "\n")

# Also a flat CSV of the quarterly series for anyone who wants to re-chart
with open(os.path.join(OUT, "quarterly_series.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["quarter"] + list(Q.keys()))
    for i in range(20):
        w.writerow([QTRS[i]] + [Q[name][i] for name in Q])

# --------------------------------------------------------------------------- SVG charts

PAL = {"blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "yellow": "#eda100",
       "red": "#e34948", "blue_lt": "#86b6ef", "red_lt": "#f2a9a8", "gray": "#c3c2b7"}
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SURF = "#fcfcfb"
FONT = "font-family=\"system-ui, -apple-system, 'Segoe UI', sans-serif\""


def nice_ticks(lo, hi, n=5):
    if lo > 0:
        lo = 0
    if hi < 0:
        hi = 0
    span = hi - lo
    raw = span / n
    mag = 10 ** math.floor(math.log10(raw)) if raw > 0 else 1
    for m in (1, 2, 2.5, 5, 10):
        step = m * mag
        if span / step <= n + 1:
            break
    t0 = math.floor(lo / step) * step
    t1 = math.ceil(hi / step) * step
    ticks = []
    t = t0
    while t <= t1 + 1e-9:
        ticks.append(round(t, 10))
        t += step
    return ticks


def money(v):
    a = abs(v)
    sgn = "-" if v < 0 else ""
    if a >= 1e6:
        s = f"{a / 1e6:.1f}".rstrip("0").rstrip(".")
        return f"{sgn}${s}M"
    if a >= 1e3:
        return f"{sgn}${a / 1e3:.0f}k"
    return f"{sgn}${a:.0f}"


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;")


def chart(out, title, subtitle, cats, series, kind="bar", stacked=True, yfmt=money,
          notes=None, width=960, height=440, label_every=1, hline=None, ymin=None, ymax=None,
          direct_labels=None):
    """Minimal SVG chart. series = [(name, values, color)]. kind = 'bar' | 'line'."""
    ml, mr, mt, mb = 70, 24, 72, 56
    pw, ph = width - ml - mr, height - mt - mb
    n = len(cats)
    # y-range
    if kind == "bar" and stacked:
        pos = [sum(max(v, 0) for _, vals, _ in series for v in [vals[i]]) for i in range(n)]
        neg = [sum(min(v, 0) for _, vals, _ in series for v in [vals[i]]) for i in range(n)]
        lo, hi = min(neg), max(pos)
    else:
        allv = [v for _, vals, _ in series for v in vals if v is not None]
        lo, hi = min(allv), max(allv)
    if hline is not None:
        lo, hi = min(lo, hline), max(hi, hline)
    if ymin is not None:
        lo = min(lo, ymin)
    if ymax is not None:
        hi = max(hi, ymax)
    ticks = nice_ticks(lo, hi)
    lo, hi = ticks[0], ticks[-1]

    def Y(v):
        return mt + ph - (v - lo) / (hi - lo) * ph

    def X(i):
        return ml + (i + 0.5) * pw / n

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" {FONT}>']
    o.append(f'<rect width="{width}" height="{height}" fill="{SURF}"/>')
    o.append(f'<text x="{ml}" y="28" font-size="17" font-weight="600" fill="{INK}">{esc(title)}</text>')
    o.append(f'<text x="{ml}" y="48" font-size="12.5" fill="{INK2}">{esc(subtitle)}</text>')
    # grid + y labels
    for t in ticks:
        y = Y(t)
        col = AXIS if abs(t) < 1e-9 else GRID
        o.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{ml + pw}" y2="{y:.1f}" stroke="{col}" stroke-width="1"/>')
        o.append(f'<text x="{ml - 8}" y="{y + 4:.1f}" font-size="11" text-anchor="end" fill="{MUTED}">{esc(yfmt(t))}</text>')
    if hline is not None:
        y = Y(hline)
        o.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{ml + pw}" y2="{y:.1f}" stroke="{INK2}" stroke-width="1"/>')
    # x labels
    for i, c in enumerate(cats):
        if i % label_every == 0:
            o.append(f'<text x="{X(i):.1f}" y="{mt + ph + 18}" font-size="11" text-anchor="middle" fill="{MUTED}">{esc(c)}</text>')
    # marks
    if kind == "bar":
        ns = 1 if stacked else len(series)
        slot = pw / n
        bw = (slot * 0.62) / ns
        for i in range(n):
            up, dn = 0.0, 0.0
            for si, (name, vals, color) in enumerate(series):
                v = vals[i]
                if v is None or v == 0:
                    continue
                if stacked:
                    x0 = X(i) - bw / 2
                    if v > 0:
                        y0, y1 = Y(up + v), Y(up)
                        up += v
                    else:
                        y0, y1 = Y(dn), Y(dn + v)
                        dn += v
                else:
                    x0 = X(i) - (ns * bw) / 2 + si * bw
                    y0, y1 = (Y(v), Y(0)) if v > 0 else (Y(0), Y(v))
                    if lo >= 0:   # bars from the axis floor when the axis has no zero below it
                        y1 = Y(lo)
                h = max(y1 - y0 - 2, 0.5)
                o.append(f'<rect x="{x0 + 1:.1f}" y="{y0 + 1:.1f}" width="{bw - 2:.1f}" height="{h:.1f}" rx="2" fill="{color}"/>')
    else:
        for name, vals, color in series:
            pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals) if v is not None)
            o.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round"/>')
            for i, v in enumerate(vals):
                if v is None:
                    continue
                o.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3.5" fill="{color}" stroke="{SURF}" stroke-width="2"/>')
    # direct labels: list of (series_idx, cat_idx, text, dy[, dx_in_bar_widths])
    for lab in (direct_labels or []):
        si, ci, text, dy = lab[:4]
        dxw = lab[4] if len(lab) > 4 else 0.0
        name, vals, color = series[si]
        v = vals[ci]
        if kind == "bar" and stacked:
            tot = sum(max(s_[1][ci], 0) for s_ in series) if v >= 0 else sum(min(s_[1][ci], 0) for s_ in series)
            yy = Y(tot) + (-6 if v >= 0 else 14)
        elif kind == "bar":
            yy = Y(v) + (-6 if v >= 0 else 14)
        else:
            yy = Y(v) + (-8 if v >= 0 else 14)
        xx = X(ci) + dxw * (pw / n) * 0.62 / (1 if stacked else len(series))
        o.append(f'<text x="{xx:.1f}" y="{yy + dy:.1f}" font-size="11" text-anchor="middle" fill="{INK2}">{esc(text)}</text>')
    # legend
    if len(series) >= 2:
        x = ml
        for name, vals, color in series:
            o.append(f'<rect x="{x}" y="{height - 18}" width="10" height="10" rx="2" fill="{color}"/>')
            o.append(f'<text x="{x + 15}" y="{height - 9}" font-size="11.5" fill="{INK2}">{esc(name)}</text>')
            x += 15 + 7.2 * len(name) + 18
    if notes:
        o.append(f'<text x="{width - mr}" y="{height - 9}" font-size="11" text-anchor="end" fill="{MUTED}">{esc(notes)}</text>')
    o.append("</svg>")
    with open(os.path.join(CHARTS, out), "w") as f:
        f.write("\n".join(o))


qlab = [q.replace(" ", " ") for q in QTRS]

# 1. Revenue by business line
chart("01_revenue_by_line.svg", "Quarterly product revenue by business line",
      "Business Line 1 has halved since its Y3 Q4 peak; Business Line 2 is now 81% of revenue. USD.",
      qlab, [("Business Line 1", bl1, PAL["blue"]), ("Business Line 2", bl2, PAL["orange"])],
      direct_labels=[(0, 11, money(rev[11]), 0), (0, 19, money(rev[19]), 0), (0, 14, money(rev[14]), 0)])

# 2. Closing contracted ARR
chart("02_closing_arr.svg", "Closing contracted ARR",
      "Growth stalled in Y4 (+13%) and fell 13% in Y5 Q1 before quarter-end deals in Y5 Q2 and Q3 lifted it. USD.",
      qlab, [("Closing contracted ARR", close_arr, PAL["blue"])], kind="line", ymin=0,
      direct_labels=[(0, 11, money(close_arr[11]), 0), (0, 15, money(close_arr[15]), 0),
                     (0, 16, money(close_arr[16]), 26), (0, 19, money(close_arr[19]), 0)])

# 3. ARR movements
chart("03_arr_movements.svg", "Quarterly ARR movements",
      "Churn plus downgrades removed 36-45% of opening ARR every year from Y3; new ARR is concentrated in quarter-end months. USD.",
      qlab, [("New ARR", new_arr, PAL["blue"]), ("Expansion", exp_arr, PAL["blue_lt"]),
             ("Downgrade", down_arr, PAL["red_lt"]), ("Churn", churn_arr, PAL["red"])],
      direct_labels=[(0, 11, money(new_arr[11] + exp_arr[11]), 0), (3, 16, money(churn_arr[16] + down_arr[16]), 0),
                     (3, 11, money(churn_arr[11] + down_arr[11]), 0), (0, 18, money(new_arr[18] + exp_arr[18]), 0)])

# 4. Retention
yrs3 = ["Y3", "Y4", "Y5"]
grr_v = [A["Gross revenue retention (ARR)"][y] * 100 for y in (2, 3, 4)]
nrr_v = [A["Net revenue retention (ARR)"][y] * 100 for y in (2, 3, 4)]
chart("04_retention.svg", "Annual ARR retention",
      "Gross 53-57%, net 60-65%. Healthy B2B SaaS: 85-90%+ gross, 100%+ net (the line).",
      yrs3, [("Gross revenue retention", grr_v, PAL["blue"]), ("Net revenue retention", nrr_v, PAL["orange"])],
      stacked=False, yfmt=lambda v: f"{v:.0f}%", hline=100, ymax=110, width=640,
      direct_labels=[(0, i, f"{grr_v[i]:.0f}%", 0, -0.5) for i in range(3)] + [(1, i, f"{nrr_v[i]:.0f}%", 0, 0.5) for i in range(3)],
      notes="line = 100%")

# 5. EBITDA corrected vs reported
chart("05_ebitda.svg", "Quarterly EBITDA, corrected",
      "Burn peaked at $4.0M in Y3 Q3; the sheet shows Y4 Q4 as -$1.56M because its formula omits four cost lines. USD.",
      qlab, [("EBITDA (corrected)", ebitda, PAL["blue"])], ymin=-4.5e6,
      direct_labels=[(0, 10, money(ebitda[10]), 0), (0, 15, "-$2.9M", 0), (0, 15, "(sheet: -$1.6M)", 13),
                     (0, 19, money(ebitda[19]), 0)])

# 6. Headcount and ARR per FTE (two panels)
chart("06a_fte.svg", "Full-time employees (quarter end)",
      "Peak 116 in Y4 Q3, 88 at the end of Y5 (-24%).", qlab, [("FTE", fte, PAL["blue"])], kind="line", ymin=0,
      yfmt=lambda v: f"{v:.0f}", width=640, height=360, label_every=2,
      direct_labels=[(0, 14, "116", 0), (0, 19, "88", 0)])
chart("06b_arr_per_fte.svg", "Contracted ARR per FTE",
      "Up 46% in Y5, from cuts more than from growth. USD.", qlab, [("ARR per FTE", [pct(a, b) for a, b in zip(close_arr, fte)], PAL["blue"])],
      kind="line", ymin=0, width=640, height=360, label_every=2,
      direct_labels=[(0, 15, money(close_arr[15] / fte[15]), 0), (0, 19, money(close_arr[19] / fte[19]), 0)])

# 7. Monthly new ARR vs churn (Y3-Y5)
mi = list(range(24, 60))
mlab = [m_hdr[i].replace(" ", " ") for i in mi]
chart("07_monthly_new_vs_churn.svg", "Monthly new ARR and churned ARR, Y3 to Y5",
      "Bookings land in month 3, 6, 9 and 12 of the year; churn clusters at month 12 and month 1, one year after the big booking months. USD.",
      mlab, [("New + expansion ARR", [m_new[i] + m_exp[i] for i in mi], PAL["blue"]),
             ("Churn + downgrade ARR", [m_churn[i] + m_down[i] for i in mi], PAL["red"])],
      label_every=3, width=1100,
      direct_labels=[(0, 11, money(m_new[35] + m_exp[35]), 0), (0, 29, money(m_new[53] + m_exp[53]), 0),
                     (0, 32, money(m_new[56] + m_exp[56]), 0), (1, 24, money(m_churn[48] + m_down[48]), 0),
                     (1, 26, money(m_churn[50] + m_down[50]), 0)])

# 8. Opex mix, annual
chart("08_opex_mix.svg", "Annual operating expenses by line (excluding COGS)",
      "People cost fell $3.7M in Y5; every non-people line rose. USD.",
      YEARS, [("People", [yr(people, y) for y in range(5)], PAL["blue"]),
              ("S&M (non-people)", [yr(sm_np, y) for y in range(5)], PAL["orange"]),
              ("G&A", [yr(ga, y) for y in range(5)], PAL["aqua"]),
              ("Rent & others", [yr(rent, y) + yr(others, y) for y in range(5)], PAL["yellow"])],
      width=640, direct_labels=[(0, y, money(yr(opex, y)), 0) for y in range(5)])

print("wrote", os.path.join(OUT, "derived_metrics.md"), "and", len(os.listdir(CHARTS)), "charts")
