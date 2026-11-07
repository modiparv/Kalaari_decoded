import sys
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.comments import Comment
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.label import DataLabelList

SRC, OUT = sys.argv[1], sys.argv[2]
wb = load_workbook(SRC)

F = "Arial"
NAVY = "1F3864"
LIGHT = "D9E1F2"
PALE = "F2F2F2"
f_norm = Font(name=F, size=10)
f_bold = Font(name=F, size=10, bold=True)
f_hdr = Font(name=F, size=10, bold=True, color="FFFFFF")
f_title = Font(name=F, size=16, bold=True, color=NAVY)
f_sub = Font(name=F, size=10, italic=True, color="595959")
f_sec = Font(name=F, size=11, bold=True, color=NAVY)
f_link = Font(name=F, size=10, color="008000")
f_input = Font(name=F, size=10, color="0000FF")
fill_hdr = PatternFill("solid", fgColor=NAVY)
fill_sec = PatternFill("solid", fgColor=LIGHT)
fill_pale = PatternFill("solid", fgColor=PALE)
fill_yel = PatternFill("solid", fgColor="FFF2CC")
thin = Side(style="thin", color="BFBFBF")
top_border = Border(top=Side(style="thin", color="000000"))
box = Border(left=thin, right=thin, top=thin, bottom=thin)

USD = '#,##0,;(#,##0,);"-"'
USDK = '#,##0;(#,##0);"-"'
PCT = '0.0%;(0.0%);"-"'
MULT = '0.0"x";(0.0"x");"-"'
NUM = '#,##0;(#,##0);"-"'
MON = '0.0;(0.0);"-"'

# ------------------------------------------------------------------ fix original sheets
s = wb["Summary MIS"]
fixes = [
    ("R16", "=R9-R10", "Corrected. Original formula was =R9-R11 (gross margin less People Cost only), which left out S&M, G&A, Rent and Others and overstated Y4 Q4 EBITDA by c.$1.31M."),
    ("O19", "=O9/O$3", "Corrected. Original formula was =O6/O$3, i.e. COGS % rather than gross margin %."),
    ("T19", "=T9/T$3", "Corrected. Original formula was =T6/T$3, i.e. COGS % rather than gross margin %."),
]
for ref, f, note in fixes:
    s[ref] = f
    s[ref].fill = fill_yel
    s[ref].comment = Comment(note, "Reviewer")
for ref in ("S12", "S13"):
    s[ref].fill = fill_yel
    s[ref].comment = Comment("S&M and G&A are identical to the cent in Y5 Q1 (682,053.99). Looks like an allocation or copy error. To be confirmed with management.", "Reviewer")

kp_ws = wb["KPIs"]
kfix = [
    ("CD14", '=IFERROR(CD7/CD13,"NA")', "Corrected. Original formula divided new ARR by (new customers + 15). It showed $33k; the true Y5 Q4 average is $88k."),
    ("CC14", '=IFERROR(CC7/CC13,"NA")', "Corrected. Original formula was =(CC7-329000)/(CC13-1). It showed $72.7k; the true Y5 M12 average is $124k."),
    ("BU14", '=IFERROR(BU7/BU13,"NA")', "Corrected. A typed number (58,412) had replaced the formula. True Y5 M6 average is $104k."),
    ("BV14", '=IFERROR(BV7/BV13,"NA")', "Corrected. A typed number (51,170) had replaced the formula. True Y5 Q2 average is $75k."),
    ("BU16", '=IFERROR(BU14/12,"NA")', "Corrected. A typed number had replaced the formula."),
    ("BV16", '=IFERROR(BV14/12,"NA")', "Corrected. A typed number had replaced the formula."),
    ("BC20", '=IFERROR((BC11-AY11)/AY11,"NA")', "Corrected. A typed growth rate (-4.8%) had replaced the formula."),
    ("BD20", '=IFERROR((BD11-AZ11)/AZ11,"NA")', "Corrected. A typed growth rate had replaced the formula."),
    ("BE20", '=IFERROR((BE11-BA11)/BA11,"NA")', "Corrected. A typed growth rate had replaced the formula."),
]
for ref, f, note in kfix:
    kp_ws[ref] = f
    kp_ws[ref].fill = fill_yel
    kp_ws[ref].comment = Comment(note, "Reviewer")
s["N3"].fill = fill_yel
s["N3"].comment = Comment("Revenue jumps 59% this quarter while subscription revenue rises about 10%, then falls back next quarter. Possibly c.$0.4M of one-off or catch-up revenue. To be confirmed.", "Reviewer")
s["C3"].fill = fill_yel
s["C3"].comment = Comment("Revenue of $120 gives a COGS ratio of exactly 66.23x. May be a typing error (about $12,029?). To be confirmed.", "Reviewer")

# ------------------------------------------------------------------ helpers
QTRS = [s.cell(row=2, column=c).value for c in range(3, 23)]
YEARS = ["Y1", "Y2", "Y3", "Y4", "Y5"]


def kcol(i):  # KPIs quarter column for quarter index i
    return L(6 + 4 * i)


def setup(ws, title, subtitle, widths):
    ws.sheet_view.showGridLines = False
    ws["B2"] = title
    ws["B2"].font = f_title
    ws["B3"] = subtitle
    ws["B3"].font = f_sub
    ws.column_dimensions["A"].width = 2
    for col, w in widths.items():
        ws.column_dimensions[col].width = w
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True


def header_row(ws, r, labels, start_col=2):
    for j, lab in enumerate(labels):
        c = ws.cell(row=r, column=start_col + j, value=lab)
        c.font = f_hdr
        c.fill = fill_hdr
        c.alignment = Alignment(horizontal="center" if j else "left", vertical="center", wrap_text=True)


def section(ws, r, text, last_col):
    for c in range(2, last_col + 1):
        ws.cell(row=r, column=c).fill = fill_sec
    ws.cell(row=r, column=2, value=text).font = f_sec


# ================================================================== Quarterly KPIs
q = wb.create_sheet("Quarterly KPIs", 0)
setup(q, "Quarterly KPIs", "USD '000 unless stated. Linked to the Summary MIS and KPIs tabs; EBITDA and gross margin recomputed from line items.",
      {"B": 38, **{L(c): 11 for c in range(3, 23)}})
QR = {}
r = 5
header_row(q, r, ["USD '000"] + QTRS)
q.freeze_panes = "C6"
r += 1


def qline(name, fn, fmt=USD, bold=False, link=False, border=False):
    global r
    q.cell(row=r, column=2, value=name).font = f_bold if bold else f_norm
    for i in range(20):
        c = q.cell(row=r, column=3 + i, value=fn(i, L(3 + i)))
        c.number_format = fmt
        c.font = f_link if link else (f_bold if bold else f_norm)
        if border:
            c.border = top_border
    QR[name] = r
    r += 1


def sm(row):
    return lambda i, c: f"='Summary MIS'!{c}{row}"


def kp(row):
    return lambda i, c: f"=KPIs!{kcol(i)}{row}"


section(q, r, "Profit & loss", 22); r += 1
qline("Revenue", sm(3), bold=True, link=True)
qline("  Business Line 1", sm(4), link=True)
qline("  Business Line 2", sm(5), link=True)
qline("  Business Line 2 share", lambda i, c: f"=IFERROR({c}{QR['  Business Line 2']}/{c}{QR['Revenue']},0)", PCT)
qline("COGS", sm(6), link=True)
qline("Gross margin", lambda i, c: f"={c}{QR['Revenue']}-{c}{QR['COGS']}", bold=True, border=True)
qline("Gross margin %", lambda i, c: f"=IFERROR({c}{QR['Gross margin']}/{c}{QR['Revenue']},0)", PCT)
qline("People cost", sm(11), link=True)
qline("Sales & marketing (non-people)", sm(12), link=True)
qline("G&A", sm(13), link=True)
qline("Rent & utilities", sm(14), link=True)
qline("Others", sm(15), link=True)
qline("Total operating expenses", lambda i, c: f"=SUM({c}{QR['People cost']}:{c}{QR['Others']})", bold=True, border=True)
qline("EBITDA", lambda i, c: f"={c}{QR['Gross margin']}-{c}{QR['Total operating expenses']}", bold=True, border=True)
qline("EBITDA margin", lambda i, c: f"=IFERROR({c}{QR['EBITDA']}/{c}{QR['Revenue']},0)", PCT)
r += 1
section(q, r, "Contracted ARR bridge", 22); r += 1
qline("Opening ARR", kp(6), link=True)
qline("New ARR", kp(7), link=True)
qline("Expansion", kp(8), link=True)
qline("Downgrade", kp(9), link=True)
qline("Churn", kp(10), link=True)
qline("Closing ARR", lambda i, c: f"=SUM({c}{QR['Opening ARR']}:{c}{QR['Churn']})", bold=True, border=True)
qline("Net new ARR", lambda i, c: f"={c}{QR['Closing ARR']}-{c}{QR['Opening ARR']}")
qline("ARR growth (QoQ)", lambda i, c: f"=IFERROR({c}{QR['Net new ARR']}/{c}{QR['Opening ARR']},0)", PCT)
qline("Gross ARR lost, % of opening", lambda i, c: f"=IFERROR(-({c}{QR['Downgrade']}+{c}{QR['Churn']})/{c}{QR['Opening ARR']},0)", PCT)
qline("Net ARR retention (quarter)", lambda i, c: f"=IFERROR(({c}{QR['Opening ARR']}+{c}{QR['Expansion']}+{c}{QR['Downgrade']}+{c}{QR['Churn']})/{c}{QR['Opening ARR']},0)", PCT)
qline("Gross retention, annualised from this quarter", lambda i, c: f"=IF({c}{QR['Opening ARR']}=0,0,(1-{c}{QR['Gross ARR lost, % of opening']})^4)", PCT)
qline("SaaS quick ratio (ARR gained / ARR lost)", lambda i, c: f"=IFERROR(({c}{QR['New ARR']}+{c}{QR['Expansion']})/-({c}{QR['Downgrade']}+{c}{QR['Churn']}),0)", MULT)
qline("Subscription ARR (closing MRR x 12)", lambda i, c: f"=KPIs!{kcol(i)}30*12", link=True)
r += 1
section(q, r, "Customers", 22); r += 1
qline("Opening customers", kp(38), NUM, link=True)
qline("New customers", kp(39), NUM, link=True)
qline("Churned customers", kp(41), NUM, link=True)
qline("Closing customers", lambda i, c: f"=SUM({c}{QR['Opening customers']}:{c}{QR['Churned customers']})", NUM, bold=True, border=True)
qline("Logo churn, % of opening", lambda i, c: f"=IFERROR(-{c}{QR['Churned customers']}/{c}{QR['Opening customers']},0)", PCT)
qline("Average ACV, new customers", lambda i, c: f"=IFERROR({c}{QR['New ARR']}/{c}{QR['New customers']},0)")
qline("Average ARR per customer", lambda i, c: f"=IFERROR({c}{QR['Closing ARR']}/{c}{QR['Closing customers']},0)")
r += 1
section(q, r, "Efficiency & team", 22); r += 1
qline("S&M cost (KPI tab, fully loaded)", kp(58), link=True)
qline("CAC per new customer", lambda i, c: f"=IFERROR({c}{QR['S&M cost (KPI tab, fully loaded)']}/{c}{QR['New customers']},0)")
qline("Sales efficiency (net new ARR / S&M)", lambda i, c: f"=IFERROR({c}{QR['Net new ARR']}/{c}{QR['S&M cost (KPI tab, fully loaded)']},0)", MULT)
qline("FTE (quarter end)", kp(59), NUM, link=True)
qline("ARR per FTE", lambda i, c: f"=IFERROR({c}{QR['Closing ARR']}/{c}{QR['FTE (quarter end)']},0)")

# ================================================================== Annual Summary
a = wb.create_sheet("Annual Summary", 0)
setup(a, "Annual Summary", "USD '000 unless stated. Built from the Quarterly KPIs tab. n.m. = not meaningful (usually the first year, which has no opening balance). See the Glossary tab for terms.",
      {"B": 44, "C": 3, **{L(c): 13 for c in range(4, 9)}, "I": 3, "J": 60})
AR = {}
r = 5
header_row(a, r, ["USD '000", ""] + YEARS + ["", "Comment"])
a.freeze_panes = "D6"
r += 1


def ycols(y):
    return L(3 + 4 * y), L(6 + 4 * y)


def aline(name, fn, fmt=USD, bold=False, border=False, comment=None):
    global r
    a.cell(row=r, column=2, value=name).font = f_bold if bold else f_norm
    for y in range(5):
        c = a.cell(row=r, column=4 + y, value=fn(y, L(4 + y)))
        c.number_format = fmt
        c.font = f_bold if bold else f_norm
        c.alignment = Alignment(horizontal="right")
        if border:
            c.border = top_border
    if comment:
        cc = a.cell(row=r, column=10, value=comment)
        cc.font = Font(name=F, size=9, italic=True, color="595959")
    AR[name] = r
    r += 1


def qsum(name):
    return lambda y, c: f"=SUM('Quarterly KPIs'!{ycols(y)[0]}{QR[name]}:{ycols(y)[1]}{QR[name]})"


def qfirst(name):
    return lambda y, c: f"='Quarterly KPIs'!{ycols(y)[0]}{QR[name]}"


def qlast(name):
    return lambda y, c: f"='Quarterly KPIs'!{ycols(y)[1]}{QR[name]}"


def growth(name):
    return lambda y, c: '="n.m."' if y == 0 else f"=IFERROR({c}{AR[name]}/{L(3 + y)}{AR[name]}-1,\"n.m.\")"


def nm(expr_fn):
    return lambda y, c: '="n.m."' if y == 0 else expr_fn(y, c)


section(a, r, "Profit & loss", 10); r += 1
aline("Revenue", qsum("Revenue"), bold=True)
aline("  Growth", growth("Revenue"), PCT)
aline("  Business Line 1", qsum("  Business Line 1"))
aline("  Business Line 2", qsum("  Business Line 2"))
aline("  Business Line 2 share", lambda y, c: f"=IFERROR({c}{AR['  Business Line 2']}/{c}{AR['Revenue']},0)", PCT,
      comment="BL1 is shrinking; BL2 now carries the business.")
aline("COGS", qsum("COGS"))
aline("Gross margin", lambda y, c: f"={c}{AR['Revenue']}-{c}{AR['COGS']}", bold=True, border=True)
aline("Gross margin %", lambda y, c: f"=IFERROR({c}{AR['Gross margin']}/{c}{AR['Revenue']},0)", PCT,
      comment="Healthy for SaaS if COGS excludes no delivery salaries. Confirm definition.")
aline("People cost", qsum("People cost"))
aline("Sales & marketing (non-people)", qsum("Sales & marketing (non-people)"))
aline("G&A", qsum("G&A"))
aline("Rent & utilities", qsum("Rent & utilities"))
aline("Others", qsum("Others"))
aline("Total operating expenses", lambda y, c: f"=SUM({c}{AR['People cost']}:{c}{AR['Others']})", bold=True, border=True,
      comment="Y5 cut came only from people cost. Every other line rose.")
aline("EBITDA", lambda y, c: f"={c}{AR['Gross margin']}-{c}{AR['Total operating expenses']}", bold=True, border=True)
aline("EBITDA margin", lambda y, c: f"=IFERROR({c}{AR['EBITDA']}/{c}{AR['Revenue']},0)", PCT)
aline("Rule of 40 (revenue growth % + EBITDA margin %)", nm(lambda y, c: f"=IFERROR(({c}{AR['Revenue'] + 1}+{c}{AR['EBITDA margin']})*100,\"n.m.\")"), '0;(0);"-"',
      comment="Healthy SaaS scores 40 or more. Shown as a plain number.")
r += 1
section(a, r, "ARR & retention", 10); r += 1
aline("Opening ARR", qfirst("Opening ARR"))
aline("New ARR", qsum("New ARR"))
aline("Expansion", qsum("Expansion"))
aline("Downgrade", qsum("Downgrade"))
aline("Churn", qsum("Churn"))
aline("Closing ARR", lambda y, c: f"=SUM({c}{AR['Opening ARR']}:{c}{AR['Churn']})", bold=True, border=True)
aline("  Growth", growth("Closing ARR"), PCT)
AR["ARR growth"] = r - 1
aline("Net new ARR", lambda y, c: f"={c}{AR['Closing ARR']}-{c}{AR['Opening ARR']}")
aline("Gross revenue retention (GRR)", nm(lambda y, c: f"=IFERROR(({c}{AR['Opening ARR']}+{c}{AR['Downgrade']}+{c}{AR['Churn']})/{c}{AR['Opening ARR']},\"n.m.\")"), PCT, bold=True,
      comment="B2B SaaS benchmark: 85-90%+. This business loses c.45% of its base every year.")
aline("Net revenue retention (NRR)", nm(lambda y, c: f"=IFERROR(({c}{AR['Opening ARR']}+{c}{AR['Expansion']}+{c}{AR['Downgrade']}+{c}{AR['Churn']})/{c}{AR['Opening ARR']},\"n.m.\")"), PCT, bold=True,
      comment="Benchmark: 100%+. Expansion is growing but is small relative to churn.")
aline("Gross retention, second half annualised", nm(lambda y, c: f"=IFERROR(1-2*-(SUM('Quarterly KPIs'!{L(5+4*y)}{QR['Downgrade']}:{L(6+4*y)}{QR['Downgrade']})+SUM('Quarterly KPIs'!{L(5+4*y)}{QR['Churn']}:{L(6+4*y)}{QR['Churn']}))/AVERAGE('Quarterly KPIs'!{L(5+4*y)}{QR['Opening ARR']}:{L(6+4*y)}{QR['Opening ARR']}),\"n.m.\")"), PCT,
      comment="Q3 and Q4 only. Y5 H2 is about 70%, much better than the full year, because Y5 Q1 alone lost $1.4M.")
aline("Dollar churn (churned ARR as % of opening ARR)", nm(lambda y, c: f"=IFERROR(-{c}{AR['Churn']}/{c}{AR['Opening ARR']},\"n.m.\")"), PCT,
      comment="Excludes downgrades. Compare with logo churn below: dollar churn is higher in Y5.")
aline("SaaS quick ratio (ARR gained / ARR lost)", nm(lambda y, c: f"=IFERROR(({c}{AR['New ARR']}+{c}{AR['Expansion']})/-({c}{AR['Downgrade']}+{c}{AR['Churn']}),\"n.m.\")"), MULT,
      comment="Healthy SaaS is 4x or more. Here about $1.6 is added for every $1 lost.")
aline("Revenue as % of average ARR", nm(lambda y, c: f"=IFERROR({c}{AR['Revenue']}/AVERAGE({c}{AR['Opening ARR']},{c}{AR['Closing ARR']}),\"n.m.\")"), PCT,
      comment="Below 100% means signed contracts are not all turning into revenue yet.")
aline("Subscription ARR (closing)", qlast("Subscription ARR (closing MRR x 12)"))
aline("Subscription ARR as % of contracted ARR", lambda y, c: f"=IFERROR({c}{AR['Subscription ARR (closing)']}/{c}{AR['Closing ARR']},0)", PCT,
      comment="The gap between the two ARR definitions is not explained in the MIS.")
r += 1
section(a, r, "Customers", 10); r += 1
aline("Opening customers", qfirst("Opening customers"), NUM)
aline("New customers", qsum("New customers"), NUM)
aline("Churned customers", qsum("Churned customers"), NUM)
aline("Closing customers", lambda y, c: f"=SUM({c}{AR['Opening customers']}:{c}{AR['Churned customers']})", NUM, bold=True, border=True)
aline("Logo churn, % of opening", nm(lambda y, c: f"=IFERROR(-{c}{AR['Churned customers']}/{c}{AR['Opening customers']},\"n.m.\")"), PCT)
aline("Average ACV, new customers", lambda y, c: f"=IFERROR({c}{AR['New ARR']}/{c}{AR['New customers']},0)")
aline("Churned ARR per churned customer", lambda y, c: f"=IFERROR({c}{AR['Churn']}/{c}{AR['Churned customers']},0)", USD,
      comment="Rising: $33k in Y3 to $63k in Y5. Lost accounts are now about the size of an average account.")
aline("Average ARR per customer (closing)", lambda y, c: f"=IFERROR({c}{AR['Closing ARR']}/{c}{AR['Closing customers']},0)")
r += 1
section(a, r, "Go-to-market efficiency & unit economics", 10); r += 1
aline("S&M cost (KPI tab, fully loaded)", qsum("S&M cost (KPI tab, fully loaded)"),
      comment="2.5-3x the S&M line in Summary MIS. Assumed to include S&M salaries. Needs reconciling.")
aline("CAC per new customer", lambda y, c: f"=IFERROR({c}{AR['S&M cost (KPI tab, fully loaded)']}/{c}{AR['New customers']},0)")
aline("CAC payback (months, gross-margin adjusted)", nm(lambda y, c: f"=IFERROR({c}{AR['S&M cost (KPI tab, fully loaded)']}/({c}{AR['New ARR']}*{c}{AR['Gross margin %']})*12,\"n.m.\")"), MON,
      comment="Months of gross profit from a new customer needed to pay back the cost of winning it.")
aline("Magic number, gross (new ARR / S&M)", nm(lambda y, c: f"=IFERROR({c}{AR['New ARR']}/{c}{AR['S&M cost (KPI tab, fully loaded)']},\"n.m.\")"), MULT,
      comment="New ARR won for each $1 of sales and marketing spend.")
aline("Magic number, net (net new ARR / S&M)", nm(lambda y, c: f"=IFERROR({c}{AR['Net new ARR']}/{c}{AR['S&M cost (KPI tab, fully loaded)']},\"n.m.\")"), MULT,
      comment="Same, after subtracting ARR lost.")
aline("Burn multiple (EBITDA burn / net new ARR)", nm(lambda y, c: f"=IFERROR(-{c}{AR['EBITDA']}/{c}{AR['Net new ARR']},\"n.m.\")"), MULT, bold=True,
      comment="Dollars of loss for each $1 of ARR added. Under 2x is good, over 3x is a concern.")
aline("Implied revenue lifetime (months, from GRR)", nm(lambda y, c: f"=IFERROR(12/(1-{c}{AR['Gross revenue retention (GRR)']}),\"n.m.\")"), MON,
      comment="KPI tab hard-codes 36 months and never uses it.")
aline("LTV (ACV x GM% x lifetime)", nm(lambda y, c: f"=IFERROR({c}{AR['Average ACV, new customers']}*{c}{AR['Gross margin %']}*{c}{AR['Implied revenue lifetime (months, from GRR)']}/12,\"n.m.\")"))
aline("LTV / CAC", nm(lambda y, c: f"=IFERROR({c}{AR['LTV (ACV x GM% x lifetime)']}/{c}{AR['CAC per new customer']},\"n.m.\")"), MULT, bold=True,
      comment="Lifetime gross profit of a customer divided by the cost to win it. Healthy is 3x or more.")
r += 1
aline("CAC, Summary MIS S&M line (floor)", lambda y, c: f"=IFERROR({c}{AR['Sales & marketing (non-people)']}/{c}{AR['New customers']},0)",
      comment="Uses the smaller S&M line, which leaves out S&M salaries. The true figure is between this and the line above.")
aline("LTV / CAC, Summary MIS S&M line (ceiling)", nm(lambda y, c: f"=IFERROR({c}{AR['LTV (ACV x GM% x lifetime)']}/{c}{AR['CAC, Summary MIS S&M line (floor)']},\"n.m.\")"), MULT,
      comment="Best case. Y5 reaches about 3x only if S&M salaries are ignored.")
r += 1
section(a, r, "Team", 10); r += 1
aline("FTE (year end)", qlast("FTE (quarter end)"), NUM)
aline("Average FTE", lambda y, c: f"=AVERAGE('Quarterly KPIs'!{ycols(y)[0]}{QR['FTE (quarter end)']}:{ycols(y)[1]}{QR['FTE (quarter end)']})", NUM)
aline("People cost per average FTE", lambda y, c: f"=IFERROR({c}{AR['People cost']}/{c}{AR['Average FTE']},0)")
aline("ARR per FTE (year end)", lambda y, c: f"=IFERROR({c}{AR['Closing ARR']}/{c}{AR['FTE (year end)']},0)",
      comment="Efficient SaaS at this scale: $150-250k.")

# ================================================================== Cash & Runway
c_ = wb.create_sheet("Cash & Runway", 0)
setup(c_, "Cash, Runway & Reconciliation", "USD '000. Balance sheet and P&L linked to the audited FS tabs; MIS figures linked to the Annual Summary.",
      {"B": 52, "C": 14, "D": 14, "E": 14, "F": 3, "G": 58})
BS, PL = "'Balance Sheet as per FS'", "'P&L as per FS'"
r = 5
section(c_, r, "Cash flow bridge, Y5 (derived from the two balance sheets)", 7); r += 1
header_row(c_, r, ["USD '000", "Y5"]); r += 1
bridge = [
    ("Net loss for the year", f"={PL}!D20"),
    ("Add back: depreciation & amortisation", f"={PL}!D14"),
    ("Increase in deferred revenue", f"={BS}!D17-{BS}!C17"),
    ("Increase in trade payables", f"=({BS}!D15+{BS}!D16)-({BS}!C15+{BS}!C16)"),
    ("Increase in provisions", f"=({BS}!D12+{BS}!D18)-({BS}!C12+{BS}!C18)"),
    ("Decrease in trade receivables", f"=-({BS}!D28-{BS}!C28)"),
    ("Decrease in short-term loans & advances", f"=-({BS}!D30-{BS}!C30)"),
    ("Decrease in other current assets", f"=-({BS}!D31-{BS}!C31)"),
    ("Increase in other non-current assets", f"=-({BS}!D25-{BS}!C25)"),
    ("Capex (change in PP&E plus D&A)", f"=-({BS}!D24-{BS}!C24+{PL}!D14)"),
    ("Equity raised (change in share capital)", f"={BS}!D8-{BS}!C8"),
]
b0 = r
for lab, f in bridge:
    c_.cell(row=r, column=2, value=lab).font = f_norm
    x = c_.cell(row=r, column=3, value=f); x.number_format = USDK; x.font = f_link
    r += 1
rows_expl = r
c_.cell(row=r, column=2, value="Explained change in cash").font = f_bold
x = c_.cell(row=r, column=3, value=f"=SUM(C{b0}:C{r - 1})"); x.number_format = USDK; x.font = f_bold; x.border = top_border
r += 1
c_.cell(row=r, column=2, value="Actual change in cash").font = f_bold
x = c_.cell(row=r, column=3, value=f"={BS}!D29-{BS}!C29"); x.number_format = USDK; x.font = f_bold
row_actual = r; r += 1
c_.cell(row=r, column=2, value="Unexplained movement").font = f_norm
x = c_.cell(row=r, column=3, value=f"=C{row_actual}-C{rows_expl}"); x.number_format = USDK
c_.cell(row=r, column=7, value="Equals the fall in reserves beyond the reported loss. Could be FX translation, a prior-period adjustment or an ESOP entry. Ask management.").font = Font(name=F, size=9, italic=True, color="595959")
r += 1
c_.cell(row=r, column=2, value="Reserves movement not through P&L").font = f_norm
x = c_.cell(row=r, column=3, value=f"=({BS}!D9-{BS}!C9)-{PL}!D20"); x.number_format = USDK
r += 1
c_.cell(row=r, column=2, value="Check: unexplained movement less reserves movement (should be zero)").font = f_norm
x = c_.cell(row=r, column=3, value=f"=C{r-2}-C{r-1}"); x.number_format = USDK
r += 2

section(c_, r, "Runway from end of Y5", 7); r += 1
header_row(c_, r, ["Basis", "Cash", "Annual burn", "Months"]); r += 1
cash = f"={BS}!D29"
ebitda_y5 = f"'Annual Summary'!H{AR['EBITDA']}"
runway = [
    ("Y5 actual cash burn (helped by prepayments and interest)", f"=-C{row_actual}"),
    ("Underlying cash burn (actual burn without the prepayment build)", f"=-C{row_actual}+C{b0 + 2}"),
    ("Y5 EBITDA burn", f"=-{ebitda_y5}/1000"),
    ("Y5 EBITDA burn net of interest income", f"=-{ebitda_y5}/1000-{PL}!D8"),
    ("Y5 Q4 EBITDA burn, annualised", f"=-'Quarterly KPIs'!V{QR['EBITDA']}*4/1000"),
]
RUNWAY_ROWS = []
for lab, f in runway:
    c_.cell(row=r, column=2, value=lab).font = f_norm
    x = c_.cell(row=r, column=3, value=cash); x.number_format = USDK; x.font = f_link
    x = c_.cell(row=r, column=4, value=f); x.number_format = USDK
    x = c_.cell(row=r, column=5, value=f"=IFERROR(C{r}/D{r}*12,0)"); x.number_format = MON; x.font = f_bold
    RUNWAY_ROWS.append(r)
    r += 1
c_.cell(row=r, column=2, value="Planning case: about 13 months (underlying burn). Prepayments unwind if renewals slip, and interest income falls with the cash balance.").font = Font(name=F, size=9, italic=True, color="595959")
r += 2

section(c_, r, "Working capital", 7); r += 1
header_row(c_, r, ["USD '000", "End Y4", "End Y5", "Change"]); r += 1
WC = [
    ("Cash and bank balances", 29),
    ("Deferred revenue", 17),
    ("Trade receivables", 28),
    ("Other non-current assets", 25),
    ("Short-term loans and advances", 30),
    ("Total shareholders' funds", 10),
]
for lab, row_ in WC:
    c_.cell(row=r, column=2, value=lab).font = f_norm
    for j, col in enumerate("CD"):
        x = c_.cell(row=r, column=3 + j, value=f"={BS}!{col}{row_}"); x.number_format = USDK; x.font = f_link
    x = c_.cell(row=r, column=5, value=f"=D{r}-C{r}"); x.number_format = USDK
    r += 1
c_.cell(row=r, column=2, value="Deferred revenue as % of contracted ARR").font = f_norm
x = c_.cell(row=r, column=3, value=f"={BS}!C17*1000/'Annual Summary'!G{AR['Closing ARR']}"); x.number_format = PCT
x = c_.cell(row=r, column=4, value=f"={BS}!D17*1000/'Annual Summary'!H{AR['Closing ARR']}"); x.number_format = PCT
c_.cell(row=r, column=7, value="Customers are prepaying more. Good for cash now, but it flatters Y5 burn by c.$3M.").font = Font(name=F, size=9, italic=True, color="595959")
r += 1
c_.cell(row=r, column=2, value="Debtor days (DSO)").font = f_norm
x = c_.cell(row=r, column=3, value=f"={BS}!C28/{PL}!C7*365"); x.number_format = '0'
x = c_.cell(row=r, column=4, value=f"={BS}!D28/{PL}!D7*365"); x.number_format = '0'
r += 2

section(c_, r, "Balance sheet ratios", 7); r += 1
header_row(c_, r, ["", "End Y4", "End Y5"]); r += 1
RATIOS = [
    ("Current ratio (current assets / current liabilities)", f"={BS}!C32/{BS}!C19", f"={BS}!D32/{BS}!D19", MULT),
    ("Current ratio excluding deferred revenue", f"={BS}!C32/({BS}!C19-{BS}!C17)", f"={BS}!D32/({BS}!D19-{BS}!D17)", MULT),
    ("Cash as % of total assets", f"={BS}!C29/{BS}!C33", f"={BS}!D29/{BS}!D33", PCT),
    ("Equity as % of total assets", f"={BS}!C10/{BS}!C33", f"={BS}!D10/{BS}!D33", PCT),
    ("Deferred revenue as % of revenue", f"={BS}!C17/{PL}!C7", f"={BS}!D17/{PL}!D7", PCT),
    ("Billings (revenue plus increase in deferred revenue)", "", f"={PL}!D7+({BS}!D17-{BS}!C17)", USDK),
    ("Interest yield on average cash", "", f"={PL}!D8/AVERAGE({BS}!C29,{BS}!D29)", PCT),
    ("Burn multiple on cash basis (cash burn / net new ARR)", "", f"=-C{row_actual}*1000/'Annual Summary'!H{AR['Net new ARR']}", MULT),
]
for lab, f1, f2, fmt in RATIOS:
    c_.cell(row=r, column=2, value=lab).font = f_norm
    for j, f in enumerate((f1, f2)):
        if f:
            x = c_.cell(row=r, column=3 + j, value=f); x.number_format = fmt
    r += 1
r += 1

section(c_, r, "MIS vs audited financial statements", 7); r += 1
header_row(c_, r, ["USD '000", "Audited FS", "MIS", "Difference"]); r += 1
rec_start = r
for yr_lab, fcol, acol in (("Y4", "C", "G"), ("Y5", "D", "H")):
    rec = [
        (f"{yr_lab} revenue from operations", f"={PL}!{fcol}7", f"='Annual Summary'!{acol}{AR['Revenue']}/1000"),
        (f"{yr_lab} employee benefits vs MIS people cost", f"={PL}!{fcol}12", f"='Annual Summary'!{acol}{AR['People cost']}/1000"),
        (f"{yr_lab} other expenses vs MIS non-people costs incl. COGS", f"={PL}!{fcol}13",
         f"=('Annual Summary'!{acol}{AR['COGS']}+SUM('Annual Summary'!{acol}{AR['Sales & marketing (non-people)']}:{acol}{AR['Others']}))/1000"),
        (f"{yr_lab} EBITDA (FS: loss less other income plus D&A)", f"={PL}!{fcol}20-{PL}!{fcol}8+{PL}!{fcol}14", f"='Annual Summary'!{acol}{AR['EBITDA']}/1000"),
    ]
    for lab, f1, f2 in rec:
        c_.cell(row=r, column=2, value=lab).font = f_norm
        x = c_.cell(row=r, column=3, value=f1); x.number_format = USDK; x.font = f_link
        x = c_.cell(row=r, column=4, value=f2); x.number_format = USDK; x.font = f_link
        x = c_.cell(row=r, column=5, value=f"=C{r}-D{r}"); x.number_format = USDK
        r += 1
c_.cell(row=rec_start, column=7, value="Y4 MIS revenue is c.$212k above the audited number. Y5 ties.").font = Font(name=F, size=9, italic=True, color="595959")
c_.cell(row=rec_start + 4, column=7, value="Y5 FS expense lines both include a +1,473 adjustment. Explanation needed.").font = Font(name=F, size=9, italic=True, color="595959")

# ================================================================== Data issues
d = wb.create_sheet("Data Issues", 0)
setup(d, "Data Issues in the MIS", "Errors and gaps found in the company file. Corrected cells are yellow in the Summary MIS and KPIs tabs, with a note on each.",
      {"B": 5, "C": 30, "D": 62, "E": 50, "F": 14})
issues = [
    ("Summary MIS, R16 (Y4 Q4 EBITDA)", "Formula took only People Cost away from gross margin. Four cost lines were left out.", "Y4 Q4 loss shown as $1.56M instead of $2.88M.", "Corrected"),
    ("Summary MIS, O19 (Y4 Q1 gross margin %)", "Formula divided COGS by revenue.", "Showed 19% instead of 81%.", "Corrected"),
    ("Summary MIS, T19 (Y5 Q2 gross margin %)", "Same error as O19.", "Showed 25% instead of 75%.", "Corrected"),
    ("KPIs, CD14 (Y5 Q4 average new deal)", "Formula divided by new customers plus 15.", "Showed $33k instead of $88k.", "Corrected"),
    ("KPIs, CC14 (Y5 M12 average new deal)", "Formula took $329k off new ARR and 1 off the customer count.", "Showed $72.7k instead of $124k.", "Corrected"),
    ("KPIs, BU14 and BV14 (Y5 M6, Y5 Q2 average new deal)", "Typed numbers replaced the formula.", "Showed $58k and $51k instead of $104k and $75k.", "Corrected"),
    ("KPIs, BU16 and BV16 (same, monthly)", "Typed numbers replaced the formula.", "Understated deal size.", "Corrected"),
    ("KPIs, BC20 to BE20 (Y4 M4 to M6 ARR growth)", "Typed growth rates replaced the formula.", "Showed a fake -4.8% month.", "Corrected"),
    ("KPIs, row 46 (customer growth)", "Some months compare with last month, others with three months back.", "Growth rates not comparable.", "Open"),
    ("Summary MIS, S12 and S13 (Y5 Q1)", "S&M and G&A are the same to the cent (682,053.99).", "One of them is wrong.", "Open"),
    ("Summary MIS, Y2 rent vs Others", "Equal to the cent in three quarters.", "Costs look allocated, not booked.", "Open"),
    ("Summary MIS, N3 (Y3 Q4 revenue)", "Revenue up 59% while subscription revenue rose about 10%.", "Possibly $0.4M of one-off revenue.", "Open"),
    ("Summary MIS, C3 (Y1 Q1 revenue)", "Revenue of $120 gives an exact 66.23x cost ratio.", "Possible typing error.", "Open"),
    ("MIS vs audit, Y4", "MIS revenue $212k above audit; costs $142k below.", "MIS made Y4 look about $0.35M better.", "Open"),
    ("Audited P&L, Y5 expenses", "The same 1,473 is added to both expense lines.", "Could be ESOP, a reclass or a double count.", "Open"),
    ("KPIs row 58 vs Summary MIS row 12", "Two S&M figures; one is 2.5 to 3 times the other.", "Cost to win a customer is $38k or $97k.", "Open"),
    ("KPIs row 51", "36-month customer life typed in and never used.", "Customer value never calculated.", "Open"),
    ("Balance sheet", "Cash and reserves fall $1.08M more than the loss explains.", "Unexplained cash movement.", "Open"),
    ("Whole pack", "No retention, cohorts, ARR by business line or cash flow statement.", "Key SaaS numbers missing.", "Open"),
]
r = 5
header_row(d, r, ["#", "Where", "Issue", "Impact", "Status"]); r += 1
for n, (w, iss, imp, st) in enumerate(issues, 1):
    vals = [n, w, iss, imp, st]
    for j, v in enumerate(vals):
        x = d.cell(row=r, column=2 + j, value=v)
        x.font = f_norm
        x.alignment = Alignment(wrap_text=True, vertical="top", horizontal="center" if j in (0, 4) else "left")
        x.border = box
    if st == "Corrected":
        d.cell(row=r, column=6).fill = PatternFill("solid", fgColor="E2EFDA")
    else:
        d.cell(row=r, column=6).fill = fill_yel
    r += 1

# ================================================================== Board questions
bq = wb.create_sheet("Board Questions", 0)
setup(bq, "Questions for Founders & Management", "For the Investment Partner to raise before the next board meeting. Ordered by priority within each area.",
      {"B": 5, "C": 18, "D": 70, "E": 55, "F": 10})
QS = [
    ("Retention", "Please share how much of each quarter's new customers' ARR is still there after 12 and 24 months, split by business line.", "Only 56% of ARR was kept in Y5. We need to see if newer customers stay longer.", "High"),
    ("Retention", "Who were the 10 biggest customers lost in Y5, and why did they leave? Y5 Q1 alone lost 16 customers and $1.2M.", "Y5 Q1 was half of the year's losses. Was it a one-off clean-up or a product problem?", "High"),
    ("Retention", "Q2 to Q4 of Y5 kept about 70% of ARR on a yearly basis. What changed, and will it last?", "If it lasts, the picture is much better than the full-year 56%.", "High"),
    ("Retention", "Which Y6 renewals are coming up each month, especially the big Y5 M6 ($1.04M) and M9 ($1.03M) deals? How healthy are they?", "These two months were half of Y5 new ARR.", "High"),
    ("Retention", "Most customers leave in month 12 or month 1. Are contracts one year long and lined up to the calendar year?", "Helps tell whether first-year customers are not renewing.", "Medium"),
    ("Retention", "Which customers grew their spend by $609k in Y5? Can this be repeated?", "Upsells are the one retention number that is improving.", "Medium"),
    ("ARR", "How do you define contracted ARR and subscription ARR? What explains the 6-18% gap?", "The board needs one clear ARR number.", "High"),
    ("ARR", "For the big M6 and M9 deals: contract length, payment terms, any discount, and are they live?", "Helps judge how solid these deals are.", "Medium"),
    ("ARR", "Y5 Q4 added only 9 new customers (average $88k each). Was that a pipeline gap or a shift to bigger deals? What does Y6 Q1 look like?", "Fewest new customers in a quarter since Y1.", "Medium"),
    ("ARR", "Why did Y3 Q4 and Y5 Q4 revenue jump far more than subscription revenue? Was any of it one-off?", "So we know what the real run-rate is.", "Medium"),
    ("Business lines", "What are Business Line 1 and 2? Is BL1 being closed down, and what happens to its customers?", "BL1 revenue is down 52% from its peak.", "High"),
    ("Business lines", "Please give margin, customer losses and cost to win a customer for each business line.", "BL2 may be healthier than the combined numbers show.", "Medium"),
    ("Sales", "Please explain the two sales and marketing figures ($5.9M and $2.3M). How many sales reps, and how many hit target?", "Cost to win a customer is $38k or $97k depending on the figure.", "High"),
    ("Sales", "How does the first-year price compare with the renewal price?", "A big price rise at renewal could explain customers leaving.", "Medium"),
    ("Costs", "Which teams did the headcount cuts come from (102 to 88 in Y5)? Was customer success cut?", "Cutting customer success could make losses worse.", "High"),
    ("Costs", "Rent and G&A went up about 20% while headcount fell. What are the lease terms?", "Next place to save money.", "Medium"),
    ("Costs", "Why did non-people costs jump to $1.9M in Y5 Q1, and why are S&M and G&A the same to the cent?", "Either a one-off or a reporting error.", "Medium"),
    ("Cash", "Please share a monthly Y6 cash plan in two cases: Y5 retention repeats, and retention reaches 70%.", "Underlying runway is about 13 months.", "High"),
    ("Cash", "What is the 1,473 added to both Y5 expense lines in the audited accounts?", "If counted twice, the loss is overstated.", "High"),
    ("Cash", "What explains the $1.08M fall in cash and reserves that is not in the P&L?", "Could be currency, an adjustment or ESOP.", "Medium"),
    ("Cash", "What is in other non-current assets ($2.6M) and loans and advances ($1.4M)? Is any of it cash?", "Changes how much money is really available.", "Medium"),
    ("Cash", "What is the fundraising plan: amount, timing and investors?", "With about 13 months of cash, the raise needs to start in Y6 Q1.", "High"),
    ("Reporting", "Please fix the MIS errors listed in the Data Issues tab and add retention, cohorts, ARR by business line and a cash flow statement.", "The board needs numbers it can rely on.", "High"),
]
r = 5
header_row(bq, r, ["#", "Area", "Question", "Why we are asking", "Priority"]); r += 1
bq.freeze_panes = "B6"
for n, (area, qq, why, pr) in enumerate(QS, 1):
    for j, v in enumerate([n, area, qq, why, pr]):
        x = bq.cell(row=r, column=2 + j, value=v)
        x.font = f_bold if j == 4 and pr == "High" else f_norm
        x.alignment = Alignment(wrap_text=True, vertical="top", horizontal="center" if j in (0, 4) else "left")
        x.border = box
        if n % 2 == 0:
            x.fill = fill_pale
    r += 1

# ================================================================== Insights
ins = wb.create_sheet("Insights", 0)
setup(ins, "Key Takeaways & Analysis", "Plain-language summary. Every number here is backed by the Annual Summary, Quarterly KPIs or Cash & Runway tabs.",
      {"B": 5, "C": 120})
blocks = [
    ("Summary", [
        "The company has $8.4M of yearly contract value (ARR) and 135 customers.",
        "It wins customers well but loses too many. In Y5 it kept only 56% of the ARR it started the year with.",
        "It still loses about $10M a year and has $11.7M of cash. Without customer prepayments, that is about 13 months of runway.",
        "Y5 Q2 to Q4 were better: about 70% of ARR kept on a yearly basis. The Y6 renewals will show if this lasts.",
    ]),
    ("1. Key takeaways", [
        "Customer losses are the main problem. Cancellations and downgrades took away $3.0M of ARR in Y5. The company needs about $3.7M of new ARR a year just to stand still.",
        "One bad quarter. Y5 Q1 lost $1.4M of ARR, about half of the year's losses. The rest of Y5 was much better.",
        "Growth costs too much. In Y5 the company lost $5.9 for every $1 of ARR it added (Y4: $17). Healthy is under $2.",
        "Revenue fell while ARR grew. ARR rose 26% but revenue fell 6% (audited: 2.5%). Business Line 1 is shrinking; Business Line 2 grew 12%.",
        "Winning a customer costs about $97k. A new customer pays about $67k a year and stays about 27 months, so it barely pays back.",
        "Cash is tighter than it looks. $3.1M of Y5 cash came from customers paying upfront and $1.2M from interest. Neither is certain next year.",
        "The MIS has many errors. Nine cells in the company file were wrong and have been corrected; ten more items need answers (see Data Issues).",
    ]),
    ("2. Trends", [
        "Revenue grew fast to $6.3M in Y4, then fell to $5.9M in Y5.",
        "Gross margin is steady at 75-80%.",
        "Losses peaked at $4.0M in Y3 Q3 and were $2.0-3.1M a quarter in Y5. Quarterly costs are down 25% from their peak.",
        "Headcount peaked at 116 (Y4 Q3) and ended Y5 at 88 (down 14% in Y5). ARR per employee rose from $65k to $95k.",
    ]),
    ("2. What is working", [
        "Upsells to existing customers grew 53% to $609k.",
        "New deals are getting bigger: $67k average in Y5, and $88k in Y5 Q4.",
        "Y5 Q2 and Q3 brought $2.8M of new ARR, the best two quarters the company has had.",
        "Losses fell 21% in Y5 while ARR grew.",
    ]),
    ("2. What is not working", [
        "Too many customers leave, mostly at the one-year mark.",
        "Lost accounts are getting bigger: $33k each in Y3, $63k in Y5.",
        "72% of new ARR is signed in the last month of a quarter, which makes results lumpy.",
        "Only 9 new customers in Y5 Q4.",
        "Rent, G&A and other costs went up about 20% while headcount fell.",
    ]),
    ("2. Key risks", [
        "Y6 renewals: the big Y5 M6 and M9 deals ($2.1M of ARR) may not renew.",
        "Cash: about 13 months of underlying runway. The raise must start soon.",
        "Next round: likely flat or down at today's retention. An insider bridge may be needed.",
        "Reporting: the board cannot fully rely on the MIS until the errors are fixed.",
        "Sales: few new customers in Q4 and a high cost to win each one.",
    ]),
    ("Decisions for the board", [
        "Plan Y6 assuming Y5 retention repeats, not a recovery.",
        "Cut yearly burn toward $6M, with a hard trigger if runway falls to 12 months.",
        "Start fundraising in Y6 Q1 and agree backup bridge terms with existing investors.",
        "Ask management for a renewal list, retention by customer group, and a monthly cash plan before the next meeting.",
        "Fix the MIS.",
    ]),
]
r = 5
for head, paras in blocks:
    ins.cell(row=r, column=2, value=head).font = f_sec
    for col in (2, 3):
        ins.cell(row=r, column=col).fill = fill_sec
    r += 1
    for p in paras:
        x = ins.cell(row=r, column=3, value=p)
        x.font = f_norm
        x.alignment = Alignment(wrap_text=True, vertical="top")
        ins.row_dimensions[r].height = 15 * max(1, -(-len(p) // 140))
        r += 1
    r += 1

# ================================================================== Dashboard
db = wb.create_sheet("Dashboard", 0)
db.sheet_view.showGridLines = False
db.column_dimensions["A"].width = 2
for col in range(2, 22):
    db.column_dimensions[L(col)].width = 12
db["B2"] = "MIS Dashboard"
db["B2"].font = f_title
db["B3"] = "Early-stage SaaS company, Y1 to Y5. USD. All tiles and charts are linked to the analysis tabs."
db["B3"].font = f_sub

A_ = "'Annual Summary'"
tiles = [
    ("Closing ARR (Y5)", f"={A_}!H{AR['Closing ARR']}/1000000", '$0.0"M"', f"={A_}!H{AR['ARR growth']}", "YoY"),
    ("Revenue (Y5)", f"={A_}!H{AR['Revenue']}/1000000", '$0.0"M"', f"={A_}!H{AR['Revenue'] + 1}", "YoY"),
    ("EBITDA (Y5)", f"={A_}!H{AR['EBITDA']}/1000000", '$0.0"M";($0.0"M")', f"={A_}!H{AR['EBITDA margin']}", "margin"),
    ("Gross retention (Y5)", f"={A_}!H{AR['Gross revenue retention (GRR)']}", '0%', f"={A_}!H{AR['Gross retention, second half annualised']}", "in H2, annualised"),
    ("Burn multiple (Y5)", f"={A_}!H{AR['Burn multiple (EBITDA burn / net new ARR)']}", '0.0"x"', f"={A_}!G{AR['Burn multiple (EBITDA burn / net new ARR)']}", "in Y4"),
    ("Cash, end Y5", "='Balance Sheet as per FS'!D29/1000", '$0.0"M"', f"='Cash & Runway'!E{RUNWAY_ROWS[1]}", "months underlying runway"),
    ("Customers (Y5)", f"={A_}!H{AR['Closing customers']}", '#,##0', f"={A_}!H{AR['Logo churn, % of opening']}", "logo churn"),
    ("LTV / CAC (Y5)", f"={A_}!H{AR['LTV / CAC']}", '0.0"x"', f"={A_}!H{AR['CAC payback (months, gross-margin adjusted)']}", "months payback"),
]
sub_fmt = {"YoY": '+0%;-0%', "margin": '0%;(0%)', "in H2, annualised": '0%', "in Y4": '0.0"x"', "months underlying runway": '0', "logo churn": '0%', "months payback": '0'}
for k, (lab, val, fmt, sub, sublab) in enumerate(tiles):
    col = 2 + (k % 4) * 3 + (k % 4)
    row = 5 + (k // 4) * 5
    for rr in range(row, row + 4):
        for cc in range(col, col + 3):
            db.cell(row=rr, column=cc).fill = fill_pale
    db.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + 2)
    db.merge_cells(start_row=row + 1, start_column=col, end_row=row + 2, end_column=col + 2)
    x = db.cell(row=row, column=col, value=lab)
    x.font = Font(name=F, size=9, bold=True, color="595959")
    x = db.cell(row=row + 1, column=col, value=val)
    x.font = Font(name=F, size=20, bold=True, color=NAVY)
    x.number_format = fmt
    x.alignment = Alignment(horizontal="left", vertical="center")
    x = db.cell(row=row + 3, column=col, value=sub)
    x.number_format = sub_fmt[sublab]
    x.font = Font(name=F, size=9, bold=True)
    x.alignment = Alignment(horizontal="left")
    x = db.cell(row=row + 3, column=col + 1, value=sublab)
    x.font = Font(name=F, size=9, color="595959")

# headline annual table on the right
tr = 5
db.cell(row=tr, column=18, value="Snapshot").font = f_sec
header_row(db, tr + 1, ["USD '000"] + YEARS, start_col=17)
db.column_dimensions["Q"].width = 26
snap = [("Revenue", "Revenue", '#,##0,'), ("Closing ARR", "Closing ARR", '#,##0,'), ("EBITDA", "EBITDA", '#,##0,;(#,##0,)'),
        ("GRR", "Gross revenue retention (GRR)", '0%'), ("NRR", "Net revenue retention (NRR)", '0%'),
        ("Customers", "Closing customers", '#,##0'), ("FTE", "FTE (year end)", '#,##0'), ("Burn multiple", "Burn multiple (EBITDA burn / net new ARR)", '0.0"x"')]
for j, (lab, key, fmt) in enumerate(snap):
    rr = tr + 2 + j
    db.cell(row=rr, column=17, value=lab).font = f_norm
    for y in range(5):
        x = db.cell(row=rr, column=18 + y, value=f"={A_}!{L(4 + y)}{AR[key]}")
        x.number_format = fmt
        x.font = f_norm
        x.border = Border(bottom=thin)

# charts, data from Quarterly KPIs
Q_ = q
cats = Reference(Q_, min_col=3, max_col=22, min_row=5)


def qref(name):
    return Reference(Q_, min_col=2, max_col=22, min_row=QR[name])


def style(ch, title, ytitle=None):
    ch.title = title
    ch.style = 10
    ch.height = 7.5
    ch.width = 16
    ch.legend.position = "b"
    if ytitle:
        ch.y_axis.title = ytitle
    ch.y_axis.majorGridlines = None
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.x_axis.tickLblPos = "low"


def color(ch, hexes):
    for sr, hx in zip(ch.series, hexes):
        sr.graphicalProperties.solidFill = hx
        sr.graphicalProperties.line.solidFill = hx


ch1 = BarChart(); ch1.type = "col"; ch1.grouping = "stacked"; ch1.overlap = 100
for n in ("  Business Line 1", "  Business Line 2"):
    ch1.add_data(qref(n), from_rows=True, titles_from_data=True)
ch1.set_categories(cats); style(ch1, "Quarterly revenue by business line (USD)")
ch1.y_axis.number_format = '$#,##0,"k"'
color(ch1, ["1F3864", "8EA9DB"])
db.add_chart(ch1, "B16")

ch2 = LineChart()
ch2.add_data(qref("Closing ARR"), from_rows=True, titles_from_data=True)
ch2.add_data(qref("Subscription ARR (closing MRR x 12)"), from_rows=True, titles_from_data=True)
ch2.set_categories(cats); style(ch2, "Closing ARR (USD)")
ch2.y_axis.number_format = '$#,##0.0,,"M"'
color(ch2, ["1F3864", "8EA9DB"])
for sr in ch2.series: sr.smooth = False
db.add_chart(ch2, "J16")

ch3 = BarChart(); ch3.type = "col"; ch3.grouping = "stacked"; ch3.overlap = 100
for n in ("New ARR", "Expansion", "Downgrade", "Churn"):
    ch3.add_data(qref(n), from_rows=True, titles_from_data=True)
ch3.set_categories(cats); style(ch3, "ARR movements by quarter (USD)")
ch3.y_axis.number_format = '$#,##0,"k"'
color(ch3, ["1F3864", "8EA9DB", "F4B183", "C00000"])
db.add_chart(ch3, "B32")

ch4 = BarChart(); ch4.type = "col"
ch4.add_data(qref("EBITDA"), from_rows=True, titles_from_data=True)
ch4.set_categories(cats); style(ch4, "Quarterly EBITDA (USD)")
ch4.y_axis.number_format = '$#,##0.0,,"M"'
color(ch4, ["C00000"])
db.add_chart(ch4, "J32")

ch5 = BarChart(); ch5.type = "col"
yr_cats = Reference(a, min_col=6, max_col=8, min_row=5)
for key in ("Gross revenue retention (GRR)", "Net revenue retention (NRR)"):
    ch5.add_data(Reference(a, min_col=2, max_col=8, min_row=AR[key]), from_rows=True, titles_from_data=True)
# keep only Y3-Y5 by pointing at those columns
ch5 = BarChart(); ch5.type = "col"
for key, lab in (("Gross revenue retention (GRR)", "GRR"), ("Net revenue retention (NRR)", "NRR")):
    ref = Reference(a, min_col=6, max_col=8, min_row=AR[key])
    ch5.add_data(ref, from_rows=True, titles_from_data=False)
from openpyxl.chart.series import SeriesLabel
ch5.series[0].tx = SeriesLabel(v="Gross revenue retention")
ch5.series[1].tx = SeriesLabel(v="Net revenue retention")
ch5.set_categories(yr_cats); style(ch5, "Annual ARR retention (benchmark: GRR 85-90%, NRR 100%+)")
ch5.y_axis.number_format = '0%'; ch5.y_axis.scaling.min = 0; ch5.y_axis.scaling.max = 1.2
ch5.dataLabels = DataLabelList(); ch5.dataLabels.showVal = True; ch5.dataLabels.showSerName = False; ch5.dataLabels.showCatName = False; ch5.dataLabels.showLegendKey = False
color(ch5, ["1F3864", "8EA9DB"])
db.add_chart(ch5, "B48")

ch6 = LineChart()
ch6.add_data(qref("FTE (quarter end)"), from_rows=True, titles_from_data=True)
ch6.set_categories(cats); style(ch6, "Headcount (FTE, quarter end)")
color(ch6, ["1F3864"])
for sr in ch6.series: sr.smooth = False
db.add_chart(ch6, "J48")

gl = wb.create_sheet("Glossary")
setup(gl, "Glossary", "Simple meanings of the terms used in this workbook.", {"B": 30, "C": 90})
TERMS = [
    ("ARR", "Annual recurring revenue. The yearly value of all signed subscription contracts."),
    ("Contracted vs subscription ARR", "Contracted ARR is what is signed. Subscription ARR is monthly billing x 12. The company does not explain the gap."),
    ("ACV", "Average yearly value of one customer's contract."),
    ("Churn", "Customers or ARR lost through cancellations."),
    ("Downgrade", "ARR lost when a customer stays but pays less."),
    ("Expansion", "Extra ARR from existing customers buying more."),
    ("Gross retention (GRR)", "Share of last year's ARR still kept, not counting upsells."),
    ("Net retention (NRR)", "Same as gross retention, but counting upsells."),
    ("Logo churn", "Share of customers lost, by count."),
    ("CAC", "Sales and marketing cost of winning one new customer."),
    ("CAC payback", "Months of gross profit from a customer needed to cover its CAC."),
    ("LTV", "Total gross profit a customer brings in before it leaves."),
    ("Magic number", "New ARR won for each $1 of sales and marketing spend."),
    ("Burn multiple", "Loss for each $1 of ARR added. Under 2x is good."),
    ("SaaS quick ratio", "ARR gained divided by ARR lost. 4x or more is healthy."),
    ("Rule of 40", "Revenue growth % plus profit margin %. 40 or more is healthy."),
    ("Deferred revenue", "Cash received from customers for service not yet delivered."),
    ("Runway", "Months until cash runs out at the current rate of loss."),
    ("n.m.", "Not meaningful. Usually the first year, which has no opening balance to compare with."),
]
r = 5
header_row(gl, r, ["Term", "Meaning"]); r += 1
for term, meaning in TERMS:
    gl.cell(row=r, column=2, value=term).font = f_bold
    x = gl.cell(row=r, column=3, value=meaning); x.font = f_norm; x.alignment = Alignment(wrap_text=True, vertical="top")
    r += 1

db.page_setup.orientation = "landscape"
db.page_setup.fitToWidth = 1
db.page_setup.fitToHeight = 1
db.sheet_properties.pageSetUpPr.fitToPage = True
db.print_area = "B2:V62"
for ws in wb.worksheets:
    ws.oddFooter.left.text = "Confidential. Draft for board discussion."
    ws.oddFooter.left.size = 8
    ws.oddFooter.right.text = "&A, page &P of &N"
    ws.oddFooter.right.size = 8

# order sheets
order = ["Dashboard", "Insights", "Annual Summary", "Quarterly KPIs", "Cash & Runway", "Board Questions", "Data Issues",
         "Glossary", "Summary MIS", "KPIs", "P&L as per FS", "Balance Sheet as per FS"]
wb._sheets = [wb[n] for n in order]
wb.active = 0
for ws in wb.worksheets:
    ws.sheet_view.tabSelected = ws.title == "Dashboard"
wb["Dashboard"].sheet_properties.tabColor = NAVY
wb["Insights"].sheet_properties.tabColor = NAVY
wb.save(OUT)
print("saved", OUT)
