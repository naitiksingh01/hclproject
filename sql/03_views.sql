-- =====================================================================
-- 03 - Reporting views (Power BI can connect to these directly)
-- =====================================================================
CREATE OR REPLACE VIEW vw_sales_flat AS
SELECT f.order_line_id, f.order_id, d.full_date AS order_date, d.year, d.quarter, d.month_no,
       d.month_name, d.year_month, d.day_name,
       c.customer_id, c.customer_name, c.segment,
       p.product_id, p.product_name, p.category, p.sub_category,
       r.state, r.region,
       f.quantity, f.unit_price, f.discount, f.sales, f.profit,
       f.payment_mode, f.ship_mode, f.ship_days, f.is_bulk_order
FROM   fact_sales f
JOIN   dim_date     d ON d.date_key    = f.date_key
JOIN   dim_customer c ON c.customer_id = f.customer_id
JOIN   dim_product  p ON p.product_id  = f.product_id
JOIN   dim_region   r ON r.region_key  = f.region_key;

CREATE OR REPLACE VIEW vw_kpi_summary AS
SELECT ROUND(SUM(sales),2)                                   AS total_sales,
       ROUND(SUM(profit),2)                                  AS total_profit,
       ROUND(100*SUM(profit)/SUM(sales),2)                   AS profit_margin_pct,
       COUNT(DISTINCT order_id)                              AS total_orders,
       COUNT(DISTINCT CASE WHEN customer_id <> 'UNKNOWN' THEN customer_id END) AS unique_customers,
       SUM(quantity)                                         AS units_sold,
       ROUND(SUM(sales)/COUNT(DISTINCT order_id),2)          AS avg_order_value,
       ROUND(100*SUM(quantity*unit_price-sales)/SUM(quantity*unit_price),2) AS avg_discount_pct
FROM   fact_sales;

CREATE OR REPLACE VIEW vw_monthly_sales AS
SELECT year_month, year, month_no,
       monthly_sales,
       LAG(monthly_sales) OVER (ORDER BY year_month)                       AS prev_month_sales,
       ROUND(100*(monthly_sales - LAG(monthly_sales) OVER (ORDER BY year_month))
             / LAG(monthly_sales) OVER (ORDER BY year_month),2)            AS mom_growth_pct,
       SUM(monthly_sales) OVER (ORDER BY year_month)                       AS running_total
FROM  (SELECT d.year_month, d.year, d.month_no, ROUND(SUM(f.sales),2) AS monthly_sales
       FROM fact_sales f JOIN dim_date d ON d.date_key = f.date_key
       GROUP BY d.year_month, d.year, d.month_no);

CREATE OR REPLACE VIEW vw_region_sales AS
SELECT r.region, ROUND(SUM(f.sales),2) AS total_sales, ROUND(SUM(f.profit),2) AS total_profit,
       COUNT(DISTINCT f.order_id) AS orders,
       ROUND(100*SUM(f.sales)/SUM(SUM(f.sales)) OVER (),2) AS sales_share_pct
FROM   fact_sales f JOIN dim_region r ON r.region_key = f.region_key
GROUP  BY r.region;

CREATE OR REPLACE VIEW vw_top_products AS
SELECT product_id, product_name, category, total_sales, units, sales_rank
FROM  (SELECT p.product_id, p.product_name, p.category,
              ROUND(SUM(f.sales),2) AS total_sales, SUM(f.quantity) AS units,
              RANK() OVER (ORDER BY SUM(f.sales) DESC) AS sales_rank
       FROM fact_sales f JOIN dim_product p ON p.product_id = f.product_id
       GROUP BY p.product_id, p.product_name, p.category)
WHERE  sales_rank <= 10;
