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

USD = '#,##0;(#,##0);"-"'
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
setup(q, "Quarterly KPIs", "All figures in USD unless stated. Linked to the Summary MIS and KPIs tabs; EBITDA and gross margin recomputed from line items.",
      {"B": 38, **{L(c): 11 for c in range(3, 23)}})
QR = {}
r = 5
header_row(q, r, ["USD"] + QTRS)
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
setup(a, "Annual Summary", "USD. Built from the Quarterly KPIs tab. n.m. = not meaningful.",
      {"B": 44, "C": 3, **{L(c): 13 for c in range(4, 9)}, "I": 3, "J": 60})
AR = {}
r = 5
header_row(a, r, ["USD", ""] + YEARS + ["", "Comment"])
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
      comment="Rising sharply: larger accounts are leaving.")
aline("Average ARR per customer (closing)", lambda y, c: f"=IFERROR({c}{AR['Closing ARR']}/{c}{AR['Closing customers']},0)")
r += 1
section(a, r, "Go-to-market efficiency & unit economics", 10); r += 1
aline("S&M cost (KPI tab, fully loaded)", qsum("S&M cost (KPI tab, fully loaded)"),
      comment="2.5-3x the S&M line in Summary MIS. Assumed to include S&M salaries. Needs reconciling.")
aline("CAC per new customer", lambda y, c: f"=IFERROR({c}{AR['S&M cost (KPI tab, fully loaded)']}/{c}{AR['New customers']},0)")
aline("CAC payback (months, gross-margin adjusted)", lambda y, c: f"=IFERROR({c}{AR['S&M cost (KPI tab, fully loaded)']}/({c}{AR['New ARR']}*{c}{AR['Gross margin %']})*12,0)", MON)
aline("Magic number, gross (new ARR / S&M)", lambda y, c: f"=IFERROR({c}{AR['New ARR']}/{c}{AR['S&M cost (KPI tab, fully loaded)']},0)", MULT)
aline("Magic number, net (net new ARR / S&M)", lambda y, c: f"=IFERROR({c}{AR['Net new ARR']}/{c}{AR['S&M cost (KPI tab, fully loaded)']},0)", MULT)
aline("Burn multiple (EBITDA burn / net new ARR)", lambda y, c: f"=IFERROR(-{c}{AR['EBITDA']}/{c}{AR['Net new ARR']},0)", MULT, bold=True,
      comment="Below 2x is good, above 3x is a concern. Y4 was very poor.")
aline("Implied customer lifetime (months, from GRR)", nm(lambda y, c: f"=IFERROR(12/(1-{c}{AR['Gross revenue retention (GRR)']}),\"n.m.\")"), MON,
      comment="KPI tab hard-codes 36 months and never uses it.")
aline("LTV (ACV x GM% x lifetime)", nm(lambda y, c: f"=IFERROR({c}{AR['Average ACV, new customers']}*{c}{AR['Gross margin %']}*{c}{AR['Implied customer lifetime (months, from GRR)']}/12,\"n.m.\")"))
aline("LTV / CAC", nm(lambda y, c: f"=IFERROR({c}{AR['LTV (ACV x GM% x lifetime)']}/{c}{AR['CAC per new customer']},\"n.m.\")"), MULT, bold=True,
      comment="Benchmark: 3x+. Under 2x means growth destroys value at current churn.")
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
c_.cell(row=r, column=7, value="Equals the fall in reserves beyond the reported loss. Most likely FX translation on INR cash. Ask management.").font = Font(name=F, size=9, italic=True, color="595959")
r += 1
c_.cell(row=r, column=2, value="Check: reserves movement not through P&L").font = f_norm
x = c_.cell(row=r, column=3, value=f"=({BS}!D9-{BS}!C9)-{PL}!D20"); x.number_format = USDK
r += 2

section(c_, r, "Runway from end of Y5", 7); r += 1
header_row(c_, r, ["Basis", "Cash", "Annual burn", "Months"]); r += 1
cash = f"={BS}!D29"
ebitda_y5 = f"'Annual Summary'!H{AR['EBITDA']}"
runway = [
    ("Y5 actual cash burn (helped by prepayments and interest)", f"=-C{row_actual}"),
    ("Y5 EBITDA burn", f"=-{ebitda_y5}/1000"),
    ("Y5 EBITDA burn less other income", f"=-{ebitda_y5}/1000-{PL}!D8"),
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
c_.cell(row=r, column=2, value="Planning case: 12-15 months. Deferred revenue unwinds if renewals slip, and interest income falls with the cash balance.").font = Font(name=F, size=9, italic=True, color="595959")
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
setup(d, "Data Issues in the MIS", "Errors and gaps found while rebuilding the numbers. Items 1-3 have been corrected in the Summary MIS tab (highlighted yellow).",
      {"B": 5, "C": 30, "D": 62, "E": 50, "F": 14})
issues = [
    ("Summary MIS, cell R16 (Y4 Q4 EBITDA)", "Formula was =R9-R11, i.e. gross margin less People Cost only. S&M, G&A, Rent and Others were left out.", "Y4 Q4 EBITDA shown as -$1.56M instead of -$2.88M. Y4 burn understated by $1.3M.", "Corrected"),
    ("Summary MIS, cell O19 (Y4 Q1 GM%)", "Formula divides COGS by revenue instead of gross margin by revenue.", "Showed 19% gross margin instead of 81%.", "Corrected"),
    ("Summary MIS, cell T19 (Y5 Q2 GM%)", "Same error as O19.", "Showed 25% gross margin instead of 75%.", "Corrected"),
    ("Summary MIS, Y5 Q1 S&M and G&A", "Both lines are exactly 682,053.99.", "One of the two is wrong, or both are allocations rather than ledger balances.", "Open"),
    ("Summary MIS, Y2 Q1-Q3 Rent vs Others", "Rent & Utilities equals Others to the cent in three quarters.", "Suggests costs are allocated by formula, not booked.", "Open"),
    ("Summary MIS vs audited P&L, Y4", "MIS revenue 6,290k vs audited 6,078k; MIS non-people costs 142k below audit.", "MIS flatters Y4 EBITDA by c.$0.35M.", "Open"),
    ("P&L as per FS, Y5 expense lines", "Employee benefits =6664+1473+11 and other expenses =6453+1473-11.", "The same 1,473k appears in both lines. Possibly a reclass counted twice.", "Open"),
    ("KPIs row 58 vs Summary MIS row 12", "KPI tab S&M cost is 2.5-3x the S&M line in Summary MIS, with no definition.", "CAC is $97k or $38k depending on which line is used.", "Open"),
    ("KPIs row 51", "Customer lifetime of 36 months is hard-coded and no formula uses it.", "LTV is never calculated; the 36 months is not supported by the churn data (27-33 months).", "Open"),
    ("KPIs row 40", "'# Dropped customers*' is zero throughout; the asterisk has no footnote.", "Definition unclear.", "Open"),
    ("KPIs rows 45-46", "Churn and growth shown only as quarterly rates. No GRR, NRR, cohorts or ARR by business line.", "The most important SaaS metrics are missing from the board pack.", "Open"),
    ("KPIs rows 11 vs 31", "Contracted ARR and subscription ARR differ by 6-18% with no explanation.", "Unclear what 'ARR' means in board materials.", "Open"),
    ("Balance sheet", "No cash flow statement. Cash and reserves fall by $1.08M more than the P&L explains.", "Burn and FX exposure are not visible.", "Open"),
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
setup(bq, "Questions for Founders & Management", "Ahead of the next board meeting. Ordered by priority within each area.",
      {"B": 5, "C": 18, "D": 70, "E": 55, "F": 10})
QS = [
    ("Retention", "Share ARR cohort retention by signing quarter (Y3 Q1 onwards) at 12 and 24 months, split by business line.", "GRR of 53-57% is the main issue. We need to know whether recent cohorts are better than older ones.", "High"),
    ("Retention", "Who were the top 10 churned accounts in Y5 (ACV, tenure, reason)? Y5 Q1 alone lost 16 customers and $1.2M of ARR.", "Churned ARR per customer has doubled to $63k, so larger accounts are leaving.", "High"),
    ("Retention", "What ARR is up for renewal each month of Y6, especially the Y5 M6 ($1.04M) and Y5 M9 ($1.03M) cohorts? What is their health today?", "These two months produced half of Y5 new ARR. Their renewal decides Y6.", "High"),
    ("Retention", "Churn peaks in month 12 and month 1 every year. Are contracts annual and calendar-aligned? How much churn is first-year deals not renewing?", "Points to quarter-end deals that do not stick.", "High"),
    ("Retention", "Which accounts drove the $609k of expansion in Y5, and is there a repeatable upsell motion?", "Expansion is the one improving retention lever.", "Medium"),
    ("Retention", "What drove downgrades of $494k (Y4) and $313k (Y5): seat cuts, module removal, or price concessions?", "Separates product value issues from commercial ones.", "Medium"),
    ("ARR definition", "Define contracted ARR vs subscription ARR. Does contracted ARR include pilots, ramps at full value, services or multi-year TCV?", "The two differ by 6-18%. The board needs one clean number.", "High"),
    ("ARR definition", "For the Y5 M6 and M9 bookings: number of customers, contract length, payment terms, discount vs list, and go-live status.", "Tests whether quarter-end deals were pulled forward or discounted.", "High"),
    ("ARR definition", "Y5 Q4 signed only 9 new customers at $33k average ACV. Pipeline gap, move down-market, or seasonality? What is the weighted Y6 Q1 pipeline?", "Weakest new-logo quarter since Y1.", "Medium"),
    ("ARR definition", "Explain revenue recognition. Why was Y5 Q4 BL2 revenue up 68% when subscription MRR grew 7%? Any one-off revenue?", "Q4 revenue should not be annualised until this is clear.", "Medium"),
    ("Business lines", "What are Business Line 1 and 2? Is BL1 being sunset, and what is the plan for its remaining customers?", "BL1 revenue is down 52% from peak; BL2 was 81% of Y5 Q4 revenue.", "High"),
    ("Business lines", "Provide gross margin, churn and CAC by business line.", "If churn sits mainly in BL1, the BL2 story is healthier than the blended numbers.", "Medium"),
    ("Go-to-market", "Reconcile S&M cost on the KPI tab ($5.9M) with the S&M line in the Summary MIS ($2.3M). Share S&M headcount, quota reps and attainment.", "CAC is $97k or $38k depending on the basis.", "High"),
    ("Go-to-market", "What discounts were given on quarter-end deals, and how does first-year price compare with renewal price?", "A price step-up at renewal would explain anniversary churn.", "Medium"),
    ("Go-to-market", "How much of S&M spend goes to retention and account management vs new-logo acquisition?", "CAC currently treats all of it as acquisition.", "Low"),
    ("Cost base", "People cost per FTE is $87-109k. Where is the team based, how much is ESOP and contractors? What was the one-off in Y5 Q2?", "Y5 Q2 people cost dipped by c.$0.5M and then recovered.", "Medium"),
    ("Cost base", "Rent rose 19% while headcount fell 24%. What are the lease commitments and break options?", "Obvious place for the next round of savings.", "Medium"),
    ("Cost base", "Explain Y5 Q1 non-people costs of $1.9M vs $1.3M in Y4 Q4, and why S&M and G&A are identical to the cent.", "Either a one-off or a reporting error.", "Medium"),
    ("Cost base", "G&A is 41% of revenue and 'Others' is 17%. Break down 'Others' and share a plan to bring G&A under 20%.", "Non-people opex rose to $6.6M on $5.9M of revenue.", "Medium"),
    ("Cost base", "Define COGS. Are any engineering or delivery salaries in COGS, or are they all in people cost?", "Changes how the 77% gross margin should be read.", "Low"),
    ("Cash & funding", "Share a monthly Y6 cash forecast with deferred revenue modelled under two cases: Y5 retention repeats, and GRR improves to 75%.", "Runway is 14-19 months and depends on renewals.", "High"),
    ("Cash & funding", "Deferred revenue is 74% of ARR (47% a year ago). What are billing terms? Were multi-year prepayments discounted?", "Prepayments flattered Y5 cash burn by c.$3M.", "High"),
    ("Cash & funding", "What sits in other non-current assets ($2.6M, up $1.5M) and short-term loans & advances ($1.4M)? Is any of it cash-like?", "Affects true liquidity.", "Medium"),
    ("Cash & funding", "Explain the $1.08M fall in cash and reserves outside the P&L. If FX, share INR-basis P&L and KPIs.", "USD trends may be partly currency.", "Medium"),
    ("Cash & funding", "Fundraising plan: amount, timing, target investors, and the metrics the company expects to show. Is an insider bridge needed?", "Process needs to start in Y6 Q1 at the latest.", "High"),
    ("Reporting", "Explain the Y4 revenue gap ($212k) between MIS and audit, and the 1,473k adjustment in both Y5 expense lines. Any audit management-letter points?", "Confidence in the numbers the board receives.", "Medium"),
    ("Reporting", "Fix the MIS: correct the EBITDA and GM% formulas; add GRR/NRR, cohorts, ARR by business line, billings, a cash flow statement and headcount by function.", "The board should not receive the current file again.", "High"),
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
setup(ins, "Key Takeaways & Analysis", "Review of the MIS and balance sheet. Figures refer to the Annual Summary, Quarterly KPIs and Cash & Runway tabs.",
      {"B": 5, "C": 120})
blocks = [
    ("Summary view", [
        "The company has c.$8.4M of contracted ARR and 135 customers, but has spent Y4 and Y5 running hard to stand still.",
        "Headline ARR grew 26% in Y5 and headcount was cut 24%. Underneath, the business keeps only 53-57% of its ARR each year (NRR 60-65%), recognised revenue fell, and EBITDA burn is still c.$10M against $11.7M of cash.",
        "Retention is the issue that matters for this board. Everything else (growth, efficiency, the next round) follows from it.",
    ]),
    ("Key takeaways", [
        "1. Churn is the core problem. Churn plus downgrades removed $2.4M (Y3), $2.8M (Y4) and $3.0M (Y5) of ARR, i.e. 43-47% of opening ARR every year. The company needs c.$3.7M of new ARR a year just to stay flat.",
        "2. Y4 was a lost year and Y5 is a partial recovery. ARR grew 13% in Y4 at a burn multiple of 17x. Y5 added $1.7M net new ARR on $10.2M of burn (5.9x). Good is below 2x.",
        "3. Growth is bought at quarter-ends and lost at anniversaries. 72% of Y5 new ARR landed in the last month of a quarter, and two months (M6 and M9) gave half the year. Churn clusters in month 12 and month 1.",
        "4. Revenue and ARR have decoupled. Contracted ARR is up 26% but audited revenue is down 2.5%. Business Line 1 has halved from its peak; Business Line 2 is 72% of Y5 revenue (81% in Y5 Q4) but grew only 12% in the year.",
        "5. Unit economics do not work yet. Fully loaded CAC is c.$97k against a $67k new-customer ACV; payback is 23 months against an implied customer life of 27-33 months. LTV/CAC is 1.2-1.6x.",
        "6. Cost cuts were people-only. People cost fell 31% in Y5 while G&A (+21%), rent (+19%) and Others (+19%) all rose. G&A alone is 41% of revenue.",
        "7. Runway is 14-19 months and leans on prepayments. Deferred revenue doubled to $6.2M (74% of ARR) and cushioned Y5 cash burn by c.$3M. No equity was raised in Y5.",
        "8. The MIS needs rework before it goes to the board again. Y4 Q4 EBITDA was overstated by $1.3M through a formula error, two GM% cells were wrong, and Y4 MIS revenue does not tie to the audit (see Data Issues).",
    ]),
    ("Financial & operating trends", [
        "Revenue: $0.1M (Y1) to $6.3M (Y4), then $5.9M in Y5. Quarterly revenue has been flat at $1.3-1.6M for seven quarters before a Y5 Q4 jump to $1.85M that subscription MRR (+7%) does not support.",
        "Mix: BL1 peaked at $737k a quarter (Y3 Q4) and is now $351k. BL2 was flat for five quarters before Y5 Q4.",
        "Gross margin: steady at 72-87% once the formula errors are fixed (Y5: 77%).",
        "Burn: EBITDA loss peaked at c.$4.0M in Y3 Q3 and was $2.0-3.1M a quarter in Y5. Cumulative EBITDA burn over five years is c.$41M.",
        "Team: FTE peaked at 116 (Y4 Q3) and ended Y5 at 88. ARR per FTE rose from $65k to $95k, mostly because of the cuts. Efficient SaaS at this scale runs at $150-250k.",
    ]),
    ("Performance drivers", [
        "Positive: expansion ARR tripled to $609k; average new-customer ACV is rising ($58k to $67k); customers are willing to prepay; Y5 H2 bookings were the strongest in the company's history.",
        "Negative: anniversary churn of larger accounts (churned ARR per lost customer doubled to $63k); dependence on a few quarter-end months; a shrinking legacy business line; non-people overheads that did not follow headcount down.",
    ]),
    ("Areas of concern / key risks", [
        "Renewal risk: the Y5 M6 and M9 cohorts ($2.1M of ARR) come up for renewal in Y6. If they behave like earlier cohorts, ARR falls and deferred revenue unwinds.",
        "Funding risk: 12-15 months of realistic runway. The raise needs to start in Y6 Q1 and will be priced on retention, not the ARR headline.",
        "Quality of revenue: two ARR definitions, a 6-18% gap between them, and revenue that does not track MRR quarter to quarter.",
        "Reporting risk: formula errors, allocated rather than booked costs, and unreconciled MIS-to-audit differences.",
        "Currency: a $1.08M movement outside the P&L suggests INR translation losses on cash; USD trends may be partly FX.",
    ]),
    ("Suggested board priorities", [
        "1. Make retention the operating plan: a GRR target (75% within four quarters, 85% within eight) with named owners.",
        "2. Decide on Business Line 1: sunset with a migration plan, or fund it to stabilise.",
        "3. Start the fundraise in Y6 Q1 and agree with co-investors what a bridge would look like if H1 retention does not improve.",
        "4. Take a further $1.5-2M out of non-people costs (rent, G&A, Others).",
        "5. Fix the MIS before the next meeting (see Board Questions #27).",
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
    ("Gross revenue retention", f"={A_}!H{AR['Gross revenue retention (GRR)']}", '0%', f"={A_}!H{AR['Net revenue retention (NRR)']}", "NRR"),
    ("Burn multiple (Y5)", f"={A_}!H{AR['Burn multiple (EBITDA burn / net new ARR)']}", '0.0"x"', f"={A_}!G{AR['Burn multiple (EBITDA burn / net new ARR)']}", "Y4"),
    ("Cash, end Y5", "='Balance Sheet as per FS'!D29/1000", '$0.0"M"', f"='Cash & Runway'!E{RUNWAY_ROWS[1]}", "months runway"),
    ("Customers", f"={A_}!H{AR['Closing customers']}", '#,##0', f"={A_}!H{AR['Logo churn, % of opening']}", "logo churn"),
    ("LTV / CAC (Y5)", f"={A_}!H{AR['LTV / CAC']}", '0.0"x"', f"={A_}!H{AR['CAC payback (months, gross-margin adjusted)']}", "mth payback"),
]
sub_fmt = {"YoY": '+0%;-0%', "margin": '0%', "NRR": '0%', "Y4": '0.0"x"', "months runway": '0', "logo churn": '0%', "mth payback": '0'}
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
ch5.dataLabels = DataLabelList(); ch5.dataLabels.showVal = True
color(ch5, ["1F3864", "8EA9DB"])
db.add_chart(ch5, "B48")

ch6 = LineChart()
ch6.add_data(qref("FTE (quarter end)"), from_rows=True, titles_from_data=True)
ch6.set_categories(cats); style(ch6, "Headcount (FTE, quarter end)")
color(ch6, ["1F3864"])
for sr in ch6.series: sr.smooth = False
db.add_chart(ch6, "J48")

# order sheets
order = ["Dashboard", "Insights", "Annual Summary", "Quarterly KPIs", "Cash & Runway", "Board Questions", "Data Issues",
         "Summary MIS", "KPIs", "P&L as per FS", "Balance Sheet as per FS"]
wb._sheets = [wb[n] for n in order]
wb.active = 0
for ws in wb.worksheets:
    ws.sheet_view.tabSelected = ws.title == "Dashboard"
wb["Dashboard"].sheet_properties.tabColor = NAVY
wb["Insights"].sheet_properties.tabColor = NAVY
wb.save(OUT)
print("saved", OUT)
