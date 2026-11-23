-- =====================================================================
-- 04 - Analysis queries (joins, GROUP BY, window functions)
-- Each query is numbered Qn; python/03_validate_sql.py cross-checks them with pandas.
-- =====================================================================

-- Q1  Headline KPIs
SELECT * FROM vw_kpi_summary;

-- Q2  Top 10 products by sales (RANK)
SELECT * FROM vw_top_products ORDER BY sales_rank;

-- Q3  Monthly trend with MoM growth and running total (LAG, running SUM)
SELECT * FROM vw_monthly_sales ORDER BY year_month;

-- Q4  Region performance and share of total
SELECT * FROM vw_region_sales ORDER BY total_sales DESC;

-- Q5  Category and sub-category drill-down with share inside category
SELECT p.category, p.sub_category,
       ROUND(SUM(f.sales),2) AS total_sales,
       ROUND(100*SUM(f.sales)/SUM(SUM(f.sales)) OVER (PARTITION BY p.category),2) AS pct_of_category
FROM   fact_sales f JOIN dim_product p ON p.product_id = f.product_id
GROUP  BY p.category, p.sub_category
ORDER  BY p.category, total_sales DESC;

-- Q6  Best product inside every category (DENSE_RANK with PARTITION BY)
SELECT category, product_name, total_sales, rank_in_category
FROM  (SELECT p.category, p.product_name, ROUND(SUM(f.sales),2) AS total_sales,
              DENSE_RANK() OVER (PARTITION BY p.category ORDER BY SUM(f.sales) DESC) AS rank_in_category
       FROM fact_sales f JOIN dim_product p ON p.product_id = f.product_id
       GROUP BY p.category, p.product_name)
WHERE  rank_in_category <= 3
ORDER  BY category, rank_in_category;

-- Q7  Year-over-year growth by quarter (LAG partitioned by quarter)
SELECT quarter, year, qtr_sales,
       LAG(qtr_sales) OVER (PARTITION BY quarter ORDER BY year) AS prev_year_sales,
       ROUND(100*(qtr_sales - LAG(qtr_sales) OVER (PARTITION BY quarter ORDER BY year))
             / LAG(qtr_sales) OVER (PARTITION BY quarter ORDER BY year),2) AS yoy_growth_pct
FROM  (SELECT d.quarter, d.year, ROUND(SUM(f.sales),2) AS qtr_sales
       FROM fact_sales f JOIN dim_date d ON d.date_key = f.date_key
       GROUP BY d.quarter, d.year)
ORDER  BY quarter, year;

-- Q8  Customer value deciles (NTILE) - decile 1 = top 10 percent spenders
SELECT decile, COUNT(*) AS customers, ROUND(SUM(cust_sales),2) AS decile_sales
FROM  (SELECT customer_id, SUM(sales) AS cust_sales,
              NTILE(10) OVER (ORDER BY SUM(sales) DESC) AS decile
       FROM fact_sales WHERE customer_id <> 'UNKNOWN' GROUP BY customer_id)
GROUP  BY decile ORDER BY decile;

-- Q9  Segment x payment mode sales matrix (conditional aggregation)
SELECT c.segment,
       ROUND(SUM(CASE WHEN f.payment_mode = 'UPI'         THEN f.sales ELSE 0 END),2) AS upi,
       ROUND(SUM(CASE WHEN f.payment_mode = 'Credit Card' THEN f.sales ELSE 0 END),2) AS credit_card,
       ROUND(SUM(CASE WHEN f.payment_mode = 'Debit Card'  THEN f.sales ELSE 0 END),2) AS debit_card,
       ROUND(SUM(CASE WHEN f.payment_mode = 'Net Banking' THEN f.sales ELSE 0 END),2) AS net_banking,
       ROUND(SUM(CASE WHEN f.payment_mode = 'COD'         THEN f.sales ELSE 0 END),2) AS cod
FROM   fact_sales f JOIN dim_customer c ON c.customer_id = f.customer_id
GROUP  BY c.segment ORDER BY c.segment;

-- Q10 Discount band impact on sales and profit margin
SELECT CASE WHEN discount = 0 THEN '0%' WHEN discount <= 0.10 THEN '1-10%'
            WHEN discount <= 0.20 THEN '11-20%' ELSE '21%+' END AS discount_band,
       COUNT(*) AS lines, ROUND(SUM(sales),2) AS total_sales,
       ROUND(100*SUM(profit)/SUM(sales),2) AS profit_margin_pct
FROM   fact_sales GROUP BY CASE WHEN discount = 0 THEN '0%' WHEN discount <= 0.10 THEN '1-10%'
            WHEN discount <= 0.20 THEN '11-20%' ELSE '21%+' END
ORDER  BY MIN(discount);
