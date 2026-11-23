# Demo Video Script (3–4 min, screen-record with OBS / Win+Alt+R / Xbox Game Bar)

| Time | Show | Say |
|---|---|---|
| 0:00 | Title slide / README | "I'm Naitik Singh Bhadoriya, roll no. 25003215410104. This is my Sales Performance Dashboard project for HCL × NASSCOM." |
| 0:20 | `docs/01_problem_statement_and_kpis.md` | Problem: dirty retail data, no trusted sales number. 8 KPIs defined. |
| 0:45 | `docs/er_star_schema.png` | Star schema: 1 fact + 4 dimensions. |
| 1:05 | Run `python python/02_clean_sales.py` | Cleaning rules R1–R10; 15,610 raw → 15,181 clean rows; nulls → 0. |
| 1:35 | Oracle SQL Developer: run `01_create_tables.sql`, load, then `05_reconciliation.sql` | Row count 15,181; total ₹241,053,486.78. |
| 2:00 | Run a few queries from `04_analysis_queries.sql` (Q2 top products, Q3 monthly trend with LAG) | Window functions RANK, LAG, NTILE. |
| 2:25 | Power BI file: cards, slicers (Year/Region/Category), drill-down Category → Sub-category | Totals equal Oracle and Python. |
| 3:15 | `reports/insights_summary.md` | Top insights: +11.6 % YoY, Oct–Nov peak, discounts above 20 % lose money. |
| 3:40 | GitHub repo page | "All code, data and reports are in the repo. Thank you." |
