# Test Cases & Acceptance Criteria (from the project list)

## Key test cases
| Test case (given) | How it is handled | Evidence |
|---|---|---|
| Null / duplicate rows | R1 duplicates removed, R3/R4/R7/R9 nulls fixed or flagged | `reports/data_quality_report.md`, null counts after = 0 |
| Negative amounts | R6 quarantined as refund entries | `reports/rejected_rows.csv` (92 rows) |
| Date format errors | R5 explicit multi-format parse, invalid dates quarantined | 967 normalised, 61 quarantined |
| Region slicer | Region slicer re-computes all KPIs & charts | `dashboard/screenshot_filtered_drilldown.png`; Power BI step 4 |

## Acceptance criteria
| Criterion | Result | Evidence |
|---|---|---|
| Top 10 products correct | ✅ SQL RANK = pandas top-10 (same names & sum) | `sql_validation.md` rows 6–8, `sql_output_Q2.csv` |
| Monthly trend correct | ✅ 24 months, max diff 0.00 | `sql_validation.md`, `sql_output_Q3.csv` |
| Total sales matches source within 0.1 % | ✅ difference 0.0000 % vs reconciliation bridge | `reconciliation_bridge.csv` |
| ≥ 5 KPIs | ✅ 8 KPIs | `docs/01_problem_statement_and_kpis.md` |
| ≥ 3 slicers | ✅ Year, Region, Category (+Segment in Power BI) | dashboard / guide |
| Drill-down | ✅ Category → Sub-category → Product | dashboard (double-click), Power BI hierarchy |
