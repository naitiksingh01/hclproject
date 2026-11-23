# Power BI Build Guide (.pbix) – 30–40 minutes

> **Why this guide exists:** a `.pbix` file can only be created inside Power BI Desktop (Windows). Everything it needs is ready: clean star-schema CSVs in `data/powerbi/`, all DAX below, and a visual reference (`dashboard/screenshot_overview.png`). Follow these steps, save as `powerbi/Sales_Performance_Dashboard.pbix`, and upload it to the repo.

## 1. Load data
Home → Get data → Text/CSV → load all five from `data/powerbi/`: `fact_sales`, `dim_date`, `dim_product`, `dim_customer`, `dim_region`.
(*Oracle option:* Get data → Oracle database → server `localhost/XEPDB1` → pick views `VW_SALES_FLAT`, tables, or the five tables. Use whichever you loaded; both give identical totals.)
In Power Query set types: `dim_date[date]` = Date, money columns = Fixed decimal, ids = Text (`date_key` can stay Whole number).

## 2. Model (Model view)
Create relationships (all one-to-many, single direction, dimension → fact):
* `dim_date[date_key]` → `fact_sales[date_key]` (active)
* `dim_date[date_key]` → `fact_sales[ship_date_key]` (inactive)
* `dim_product[product_id]` → `fact_sales[product_id]`
* `dim_customer[customer_id]` → `fact_sales[customer_id]`
* `dim_region[region_key]` → `fact_sales[region_key]`
Select `dim_date` → Table tools → **Mark as date table** (column `date`). Sort `month_name` by `month_no`.
Hierarchies: `dim_product` Category → Sub-category → Product name (drill-down); `dim_region` Region → State; `dim_date` Year → Quarter → Month.

## 3. DAX measures (New measure on `fact_sales`)
```DAX
Total Sales      = SUM ( fact_sales[sales] )
Total Profit     = SUM ( fact_sales[profit] )
Profit Margin %  = DIVIDE ( [Total Profit], [Total Sales] )
Total Orders     = DISTINCTCOUNT ( fact_sales[order_id] )
Avg Order Value  = DIVIDE ( [Total Sales], [Total Orders] )
Units Sold       = SUM ( fact_sales[quantity] )
Unique Customers = CALCULATE ( DISTINCTCOUNT ( fact_sales[customer_id] ), fact_sales[customer_id] <> "UNKNOWN" )
Avg Discount %   = DIVIDE ( SUMX ( fact_sales, fact_sales[quantity]*fact_sales[unit_price] - fact_sales[sales] ),
                            SUMX ( fact_sales, fact_sales[quantity]*fact_sales[unit_price] ) )
Sales PY         = CALCULATE ( [Total Sales], SAMEPERIODLASTYEAR ( dim_date[date] ) )
Sales YoY %      = DIVIDE ( [Total Sales] - [Sales PY], [Sales PY] )
Sales PM         = CALCULATE ( [Total Sales], DATEADD ( dim_date[date], -1, MONTH ) )
Sales MoM %      = DIVIDE ( [Total Sales] - [Sales PM], [Sales PM] )
Sales Rank Product = RANKX ( ALL ( dim_product[product_name] ), [Total Sales], , DESC )
Discount Band    = -- calculated column on fact_sales
    SWITCH ( TRUE(), fact_sales[discount] = 0, "0%", fact_sales[discount] <= 0.10, "1-10%",
                     fact_sales[discount] <= 0.20, "11-20%", "21%+" )
```

## 4. Report page 1 – "Sales Overview" (layout like `screenshot_overview.png`)
| Visual | Fields |
|---|---|
| 6 × **Card** (≥5 KPIs required) | Total Sales, Total Profit, Profit Margin %, Total Orders, Avg Order Value, Unique Customers |
| **Line chart** (trend) | X: `dim_date[year_month]`, Y: Total Sales |
| **Bar / map** (regional) | `dim_region[region]` (drill to `state`), Total Sales |
| **Column chart** (drill-down) | `dim_product` hierarchy Category → Sub-category, Total Sales (use the drill-down arrows) |
| **Bar chart** Top 10 products | `product_name`, Total Sales, Visual filter → Top N = 10 by Total Sales |
| **Donut** | `payment_mode`, Total Sales |
| **Slicers (≥3 required)** | `dim_date[year]`, `dim_region[region]`, `dim_product[category]`, optional `dim_customer[segment]` |

## 5. Page 2 – "Profit & Discount"
Clustered column: `Discount Band` × Profit Margin %; Matrix: Category × Region with Total Sales and Profit Margin % (conditional-format red for negative); Scatter: product (Total Sales vs Profit Margin %); Line: Sales YoY % by `quarter`.

## 6. Page 3 – "Customer & Payment"
Bar: `dim_customer[segment]` Total Sales; Table: top 10 customers (`customer_name`, Total Sales, Total Orders) with Top N = 10 filter, excluding `UNKNOWN`; Stacked bar: `payment_mode` × `segment`.

## 7. Drill-down & polish
Turn on **Drill through** for `product_name` (new page "Product detail"). Add tooltips, titles, theme (View → Themes → Browse → `powerbi/theme_sales.json`). Add a text box on page 1: *Naitik Singh Bhadoriya · 25003215410104 · Synthetic data*.

## 8. Reconcile (fill the table in `reports/data_quality_report.md`)
Clear all slicers → cards must read **Total Sales = 241,053,486.78 (₹24.11 Cr)**, **Total Orders = 8,947**, **Unique Customers = 1,595**. Set Year = 2024 → ₹12.71 Cr. If a number differs, check relationships and that `customer_id` is Text.

## 9. Publish for HCL
Save `.pbix` → File → Export → also export page screenshots/PDF (File → Export → PDF) for the portal and repo.
