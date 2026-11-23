-- =====================================================================
-- 05 - Reconciliation: CSV  <->  Oracle  <->  Power BI
-- Expected values come from reports/reconciliation_bridge.csv and dq_summary.json
-- =====================================================================
-- R1 row count (expected 15181)
SELECT COUNT(*) AS fact_rows FROM fact_sales;

-- R2 total sales (expected 241053486.78; tolerance 0.1 percent = 240812433.29 .. 241294540.27)
SELECT ROUND(SUM(sales),2) AS total_sales FROM fact_sales;

-- R3 orphan check - every FK resolves (expected 0 rows)
SELECT f.order_line_id FROM fact_sales f
LEFT JOIN dim_product  p ON p.product_id  = f.product_id
LEFT JOIN dim_customer c ON c.customer_id = f.customer_id
LEFT JOIN dim_region   r ON r.region_key  = f.region_key
WHERE p.product_id IS NULL OR c.customer_id IS NULL OR r.region_key IS NULL;

-- R4 duplicate check on natural key (expected 0 rows)
SELECT order_id, product_id, date_key, customer_id, quantity, unit_price, COUNT(*) AS n
FROM fact_sales GROUP BY order_id, product_id, date_key, customer_id, quantity, unit_price
HAVING COUNT(*) > 1;

-- R5 sales formula check (expected 0 rows)
SELECT order_line_id FROM fact_sales
WHERE ABS(sales - ROUND(quantity*unit_price*(1-discount),2)) > 0.02;

-- R6 per-year totals (compare with Power BI card filtered by year)
SELECT d.year, ROUND(SUM(f.sales),2) AS sales FROM fact_sales f JOIN dim_date d ON d.date_key=f.date_key GROUP BY d.year ORDER BY d.year;
