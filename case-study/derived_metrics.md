# Derived metrics (rebuilt from raw inputs)

All USD, in thousands unless marked. Rebuilt by `analysis.py` from the hard-coded input rows; the sheet's own formula rows are not used because several are wrong (see MIS_Analysis.md).

## Annual view

| Metric | Y1 | Y2 | Y3 | Y4 | Y5 |
|---|---:|---:|---:|---:|---:|
| Revenue (MIS) | 128 | 1,477 | 4,285 | 6,290 | 5,925 |
|   Business Line 1 | 112 | 991 | 2,206 | 2,470 | 1,632 |
|   Business Line 2 | 16 | 486 | 2,080 | 3,820 | 4,293 |
| Gross margin | 36 | 1,194 | 3,486 | 4,742 | 4,566 |
| Gross margin % | 28% | 81% | 81% | 75% | 77% |
| People cost | 1,309 | 3,549 | 9,587 | 11,816 | 8,148 |
| S&M (non-people, Summary MIS) | 260 | 737 | 2,151 | 2,316 | 2,325 |
| S&M (KPI sheet basis) | 651 | 2,169 | 5,163 | 6,498 | 5,901 |
| G&A | 312 | 721 | 1,661 | 2,000 | 2,429 |
| Rent & utilities | 156 | 309 | 627 | 702 | 839 |
| Others | 145 | 316 | 723 | 832 | 987 |
| Total opex (ex COGS) | 2,182 | 5,633 | 14,749 | 17,665 | 14,727 |
| EBITDA (corrected) | -2,145 | -4,439 | -11,263 | -12,923 | -10,161 |
| EBITDA (as shown in sheet) | -2,145 | -4,439 | -11,263 | -11,611 | -10,161 |
| EBITDA margin | -1,676% | -301% | -263% | -205% | -171% |
| Closing contracted ARR | 610 | 3,287 | 5,910 | 6,661 | 8,385 |
| Closing subscription ARR (MRR x 12) | 511 | 2,736 | 4,816 | 6,064 | 7,680 |
| New ARR | 621 | 2,979 | 3,928 | 3,125 | 4,072 |
| Expansion ARR | 0 | 50 | 115 | 398 | 609 |
| Downgrade ARR | 0 | 0 | -123 | -494 | -313 |
| Churned ARR | -10 | -353 | -1,297 | -2,277 | -2,643 |
| Net new ARR | 610 | 2,676 | 2,623 | 751 | 1,724 |
| Gross revenue retention (ARR) | n/a | 42% | 57% | 53% | 56% |
| Net revenue retention (ARR) | n/a | 50% | 60% | 60% | 65% |
| New logos | 31 | 73 | 68 | 52 | 61 |
| Churned logos | 2 | 14 | 39 | 53 | 42 |
| Closing customers | 29 | 88 | 117 | 116 | 135 |
| Logo churn (annual, on opening) | n/a | 48% | 44% | 45% | 36% |
| Avg new ACV | 20 | 41 | 58 | 60 | 67 |
| Avg ARR per customer (closing) | 21 | 37 | 51 | 57 | 62 |
| CAC (KPI S&M / new logos) | 21 | 30 | 76 | 125 | 97 |
| CAC (Summary S&M / new logos) | 8 | 10 | 32 | 45 | 38 |
| CAC payback, months (KPI S&M, GM-adjusted) | 44 | 11 | 19 | 33 | 23 |
| Magic number, gross (new ARR / KPI S&M) | 1.0x | 1.4x | 0.8x | 0.5x | 0.7x |
| Magic number, net (net new ARR / KPI S&M) | 0.9x | 1.2x | 0.5x | 0.1x | 0.3x |
| Burn multiple (EBITDA burn / net new ARR) | 3.5x | 1.7x | 4.3x | 17.2x | 5.9x |
| Closing FTE | 30 | 71 | 109 | 102 | 88 |
| ARR per FTE (closing) | 20 | 46 | 54 | 65 | 95 |
| People cost per avg FTE | 52 | 59 | 94 | 109 | 87 |

## Year-on-year growth

| Metric | Y2 | Y3 | Y4 | Y5 |
|---|---:|---:|---:|---:|
| Revenue (MIS) | 1,054% | 190% | 47% | -6% |
|   Business Line 1 | 787% | 123% | 12% | -34% |
|   Business Line 2 | 2,878% | 328% | 84% | 12% |
| Closing contracted ARR | 438% | 80% | 13% | 26% |
| Closing subscription ARR (MRR x 12) | 435% | 76% | 26% | 27% |
| New ARR | 380% | 32% | -20% | 30% |
| Total opex (ex COGS) | 158% | 162% | 20% | -17% |
| People cost | 171% | 170% | 23% | -31% |
| Closing FTE | 137% | 54% | -6% | -14% |

## Quarterly view (Y3 Q1 to Y5 Q4)

| Metric | Y3 Q1 | Y3 Q2 | Y3 Q3 | Y3 Q4 | Y4 Q1 | Y4 Q2 | Y4 Q3 | Y4 Q4 | Y5 Q1 | Y5 Q2 | Y5 Q3 | Y5 Q4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Revenue | 769 | 905 | 1,009 | 1,602 | 1,562 | 1,586 | 1,641 | 1,501 | 1,479 | 1,321 | 1,276 | 1,849 |
|   BL1 | 446 | 498 | 525 | 737 | 687 | 650 | 607 | 525 | 488 | 409 | 383 | 351 |
|   BL2 | 323 | 407 | 484 | 865 | 874 | 936 | 1,034 | 976 | 991 | 911 | 894 | 1,498 |
| Gross margin % (corrected) | 76% | 79% | 79% | 87% | 81% | 75% | 73% | 72% | 76% | 75% | 75% | 81% |
| Gross margin % (as shown) | 76% | 79% | 79% | 87% | 19% | 75% | 73% | 72% | 76% | 25% | 75% | 81% |
| Opex ex COGS | 2,157 | 3,160 | 4,766 | 4,665 | 4,988 | 4,416 | 4,300 | 3,960 | 4,241 | 3,000 | 3,741 | 3,745 |
|   People | 1,402 | 2,054 | 3,098 | 3,032 | 3,337 | 2,954 | 2,876 | 2,649 | 2,346 | 1,660 | 2,070 | 2,072 |
|   S&M (Summary) | 294 | 453 | 717 | 686 | 677 | 585 | 555 | 498 | 682 | 456 | 585 | 602 |
|   G&A | 257 | 365 | 517 | 522 | 545 | 497 | 498 | 459 | 682 | 509 | 618 | 619 |
|   Rent | 98 | 133 | 200 | 196 | 198 | 175 | 171 | 157 | 246 | 174 | 217 | 201 |
|   Others | 106 | 155 | 234 | 229 | 231 | 205 | 199 | 197 | 284 | 201 | 251 | 251 |
| EBITDA (corrected) | -1,574 | -2,446 | -3,966 | -3,277 | -3,717 | -3,230 | -3,100 | -2,876 | -3,116 | -2,007 | -2,789 | -2,250 |
| EBITDA (as shown) | -1,574 | -2,446 | -3,966 | -3,277 | -3,717 | -3,230 | -3,100 | -1,565 | -3,116 | -2,007 | -2,789 | -2,250 |
| Opening ARR | 3,287 | 3,840 | 4,402 | 4,876 | 5,910 | 6,309 | 6,369 | 6,915 | 6,661 | 5,776 | 6,890 | 8,237 |
| New ARR | 670 | 795 | 674 | 1,789 | 947 | 613 | 917 | 648 | 476 | 1,358 | 1,445 | 794 |
| Expansion | 18 | 19 | 55 | 24 | 54 | 79 | 53 | 211 | 49 | 160 | 324 | 75 |
| Downgrade | -67 | -2 | 0 | -53 | -105 | 0 | -93 | -296 | -235 | -47 | -18 | -14 |
| Churn | -67 | -250 | -255 | -726 | -496 | -632 | -332 | -817 | -1,175 | -358 | -404 | -706 |
| Closing ARR | 3,840 | 4,402 | 4,876 | 5,910 | 6,309 | 6,369 | 6,915 | 6,661 | 5,776 | 6,890 | 8,237 | 8,385 |
| QoQ ARR growth | 17% | 15% | 11% | 21% | 7% | 1% | 9% | -4% | -13% | 19% | 20% | 2% |
| Gross ARR churn % of opening (qtr) | 4% | 7% | 6% | 16% | 10% | 10% | 7% | 16% | 21% | 7% | 6% | 9% |
| Net ARR retention (qtr) | 96% | 94% | 95% | 85% | 91% | 91% | 94% | 87% | 80% | 96% | 99% | 92% |
| New logos | 14 | 16 | 16 | 22 | 17 | 11 | 12 | 12 | 15 | 18 | 19 | 9 |
| Churned logos | 5 | 6 | 11 | 17 | 12 | 11 | 13 | 17 | 16 | 6 | 8 | 12 |
| Closing customers | 97 | 107 | 112 | 117 | 122 | 122 | 121 | 116 | 115 | 127 | 138 | 135 |
| Logo churn % of opening (qtr) | 6% | 6% | 10% | 15% | 10% | 9% | 11% | 14% | 14% | 5% | 6% | 9% |
| S&M (KPI basis) | 898 | 1,296 | 1,264 | 1,705 | 1,901 | 1,727 | 1,467 | 1,403 | 1,484 | 1,472 | 1,423 | 1,523 |
| CAC (KPI S&M / new logos) | 64 | 81 | 79 | 78 | 112 | 157 | 122 | 117 | 99 | 82 | 75 | 169 |
| FTE | 90 | 105 | 106 | 109 | 103 | 113 | 116 | 102 | 101 | 96 | 91 | 88 |
| ARR per FTE | 43 | 42 | 46 | 54 | 61 | 56 | 60 | 65 | 57 | 72 | 91 | 95 |
| Revenue / (sum of monthly MRR in qtr) | 96% | 91% | 94% | 136% | 110% | 110% | 108% | 95% | 105% | 95% | 73% | 94% |

## MIS vs audited financial statements (USD '000)

| Line | Y4 FS | Y4 MIS | Diff | Y5 FS | Y5 MIS | Diff |
|---|---:|---:|---:|---:|---:|---:|
| Revenue from operations | 6,078 | 6,290 | -212 | 5,924 | 5,925 | -1 |
| Employee benefits vs MIS People cost | 11,816 | 11,816 | 0 | 8,148 | 8,148 | -0 |
| Other expenses vs MIS COGS+S&M+G&A+Rent+Others | 7,538 | 7,396 | 142 | 7,915 | 7,938 | -23 |
| EBITDA (FS: loss - other income + D&A) vs MIS | -13,276 | -12,923 | -353 | -10,139 | -10,161 | 22 |

## Indirect cash flow for Y5, derived from the two balance sheets (USD '000)

| Item | USD '000 |
|---|---:|
| Net loss | -8,917 |
| Add back D&A | 22 |
| Increase in deferred revenue | 3,061 |
| Increase in trade payables | 117 |
| Increase in provisions | 75 |
| Decrease in trade receivables | 23 |
| Decrease in short-term loans & advances | 597 |
| Decrease in other current assets | 207 |
| Increase in other non-current assets | -1,480 |
| Capex (change in PPE plus D&A) | -19 |
| Share capital issued | 0 |
| **Explained change in cash** | **-6,314** |
| **Actual change in cash** | **-7,395** |
| Unexplained (matches reserves movement not in P&L: -1,081) | -1,081 |

## Runway at end of Y5 (cash USD 11,726k)

| Basis | Annual burn (USD '000) | Months of runway |
|---|---:|---:|
| Y5 actual cash burn (helped by +3,061 deferred revenue and 1,244 other income) | 7,395 | 19 |
| Y5 EBITDA burn | 10,161 | 14 |
| Y5 EBITDA burn less Y5 other income | 8,917 | 16 |
| Y5 Q4 EBITDA burn, annualised | 8,998 | 16 |

## Unit economics (Y5, fully loaded KPI-sheet S&M)

| Item | Value |
|---|---:|
| Average new-logo ACV | $66.8k |
| Gross margin | 77% |
| CAC per new logo (KPI S&M basis) | $96.7k |
| CAC per new logo (Summary MIS S&M basis) | $38.1k |
| CAC payback, gross-margin adjusted | 23 months |
| Implied customer lifetime from ARR gross retention (56%) | 27 months |
| Implied customer lifetime from logo churn (36%) | 33 months |
| Sheet's hard-coded lifetime assumption | 36 months |
| LTV / CAC using ARR-retention lifetime | 1.2x (LTV $116k) |
| LTV / CAC using logo-churn lifetime | 1.5x (LTV $142k) |
| LTV / CAC using 36-month assumption | 1.6x (LTV $154k) |
